from pathlib import Path

import joblib
import numpy as np

import app.retraining.local_serving_rollback as rollback_module
from app.model_registry import (
    build_model_version_metadata,
    find_champion_model_versions,
    get_model_versions,
    save_model_version_metadata,
)
from app.retraining.candidate_run_metadata import (
    CANDIDATE_LOCAL_SERVING_ROLLED_BACK,
    CANDIDATE_LOCAL_SERVING_UPDATED,
    build_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)
from app.retraining.local_serving_rollback import (
    LocalServingRollbackError,
    rollback_local_retraining_serving,
)
from app.retraining.local_serving_update import LocalServingUpdateError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "lessons.md"


class DummyChurnModel:
    def __init__(self, prediction: int):
        self.prediction = prediction

    def predict(self, features):
        return np.full(len(features), self.prediction, dtype=int)

    def predict_proba(self, features):
        positive = 0.8 if self.prediction == 1 else 0.2
        return np.array([[1 - positive, positive] for _ in range(len(features))])


def test_local_retraining_rollback_restores_target_and_validates_serving(
    tmp_path,
) -> None:
    runs_dir = tmp_path / "runs"
    registry_dir = tmp_path / "registry"
    target_path, retraining_path = _save_registry_versions(registry_dir, tmp_path)
    metadata = _updated_metadata(
        run_id="retrain-rollback",
        target_path=target_path,
        retraining_path=retraining_path,
    )
    save_candidate_retraining_run_metadata(metadata, runs_dir=runs_dir)

    report, updated_metadata, report_path = rollback_local_retraining_serving(
        run_id="retrain-rollback",
        reason="Prediction quality incident.",
        rolled_back_by="alauddin",
        runs_dir=runs_dir,
        registry_dir=registry_dir,
        rolled_back_at="2026-06-19T00:00:00+00:00",
    )

    champions = find_champion_model_versions(
        "customer_churn_model",
        registry_dir,
    )
    versions = get_model_versions("customer_churn_model", registry_dir)

    assert len(champions) == 1
    assert champions[0]["model_version"] == "v1-old"
    assert any(
        version["model_version"] == "v1-retrain-test"
        and version["status"] == "archived"
        for version in versions
    )
    assert report["restored_champion"]["model_version"] == "v1-old"
    assert report["archived_retraining_champion"]["model_version"] == (
        "v1-retrain-test"
    )
    assert report["readiness_validation"]["status"] == "ready"
    assert report["prediction_validation"]["status"] == "success"
    assert report["prediction_validation"]["model_version"] == "v1-old"
    assert report["cloud_run_update"] == "not_performed"
    assert updated_metadata["status"] == CANDIDATE_LOCAL_SERVING_ROLLED_BACK
    assert updated_metadata["promotion"]["serving_update"] == (
        "local_registry_rolled_back"
    )
    assert updated_metadata["promotion"]["local_active_model_version"] == "v1-old"
    assert report_path.is_file()


def test_local_retraining_rollback_requires_local_serving_update(tmp_path) -> None:
    metadata = _updated_metadata(
        run_id="retrain-blocked",
        target_path=tmp_path / "old.pkl",
        retraining_path=tmp_path / "new.pkl",
    )
    metadata["status"] = "candidate_serving_handoff_validated"
    save_candidate_retraining_run_metadata(metadata, runs_dir=tmp_path / "runs")

    try:
        rollback_local_retraining_serving(
            run_id="retrain-blocked",
            reason="Test rollback.",
            rolled_back_by="alauddin",
            runs_dir=tmp_path / "runs",
            registry_dir=tmp_path / "registry",
        )
    except LocalServingRollbackError as exc:
        assert CANDIDATE_LOCAL_SERVING_UPDATED in str(exc)
    else:
        raise AssertionError("Expected LocalServingRollbackError.")


def test_local_retraining_rollback_rejects_mismatched_target(tmp_path) -> None:
    runs_dir = tmp_path / "runs"
    registry_dir = tmp_path / "registry"
    target_path, retraining_path = _save_registry_versions(registry_dir, tmp_path)
    metadata = _updated_metadata(
        run_id="retrain-mismatch",
        target_path=target_path,
        retraining_path=retraining_path,
    )
    metadata["promotion"]["rollback_target"]["artifact_uri"] = "wrong.pkl"
    save_candidate_retraining_run_metadata(metadata, runs_dir=runs_dir)

    try:
        rollback_local_retraining_serving(
            run_id="retrain-mismatch",
            reason="Test rollback.",
            rolled_back_by="alauddin",
            runs_dir=runs_dir,
            registry_dir=registry_dir,
        )
    except LocalServingRollbackError as exc:
        assert "artifact URI does not match" in str(exc)
    else:
        raise AssertionError("Expected rollback target mismatch failure.")


def test_local_retraining_rollback_restores_retraining_champion_on_failure(
    tmp_path,
    monkeypatch,
) -> None:
    runs_dir = tmp_path / "runs"
    registry_dir = tmp_path / "registry"
    target_path, retraining_path = _save_registry_versions(registry_dir, tmp_path)
    metadata = _updated_metadata(
        run_id="retrain-failed-rollback",
        target_path=target_path,
        retraining_path=retraining_path,
    )
    save_candidate_retraining_run_metadata(metadata, runs_dir=runs_dir)

    def fail_validation(**kwargs):
        raise LocalServingUpdateError("simulated rollback validation failure")

    monkeypatch.setattr(
        rollback_module,
        "_validate_updated_serving",
        fail_validation,
    )

    try:
        rollback_local_retraining_serving(
            run_id="retrain-failed-rollback",
            reason="Test rollback failure.",
            rolled_back_by="alauddin",
            runs_dir=runs_dir,
            registry_dir=registry_dir,
        )
    except LocalServingRollbackError as exc:
        assert "simulated rollback validation failure" in str(exc)
    else:
        raise AssertionError("Expected rollback validation failure.")

    champions = find_champion_model_versions(
        "customer_churn_model",
        registry_dir,
    )
    versions = get_model_versions("customer_churn_model", registry_dir)

    assert len(champions) == 1
    assert champions[0]["model_version"] == "v1-retrain-test"
    assert any(
        version["model_version"] == "v1-old" and version["status"] == "archived"
        for version in versions
    )


def test_v10_c10_docs_mention_retraining_rollback_and_cloud_boundary() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "python -m app.rollback_local_retraining_model --run-id <run_id>" in readme
    assert "retraining_runs/<run_id>/local_serving_rollback_report.json" in readme
    assert "V10-C10: Local Retraining Rollback Validation" in implementation
    assert "A rollback also needs validation" in lessons
    assert "Cloud Run remains unchanged" in lessons


def _save_registry_versions(
    registry_dir: Path,
    tmp_path: Path,
) -> tuple[Path, Path]:
    target_path = tmp_path / "old-model.pkl"
    retraining_path = tmp_path / "retraining-model.pkl"
    joblib.dump(DummyChurnModel(0), target_path)
    joblib.dump(DummyChurnModel(1), retraining_path)

    target = build_model_version_metadata(
        model_name="customer_churn_model",
        model_version="v1-old",
        status="archived",
        mlflow_run_id="old-run",
        candidate_name="old-candidate",
        model_type="decision_tree",
        dataset_name="customer_churn",
        dataset_version="v1",
        dataset_checksum="abc123",
        metrics={"f1": 0.9},
        artifact_uri=str(target_path),
    )
    retraining = build_model_version_metadata(
        model_name="customer_churn_model",
        model_version="v1-retrain-test",
        status="champion",
        mlflow_run_id="retrain-test",
        candidate_name="v10_retraining_candidate",
        model_type="logistic_regression",
        dataset_name="customer_churn",
        dataset_version="v1",
        dataset_checksum="abc123",
        metrics={"f1": 1.0},
        artifact_uri=str(retraining_path),
    )
    save_model_version_metadata(target, output_dir=registry_dir)
    save_model_version_metadata(retraining, output_dir=registry_dir)
    return target_path, retraining_path


def _updated_metadata(
    *,
    run_id: str,
    target_path: Path,
    retraining_path: Path,
) -> dict:
    metadata = build_candidate_retraining_run_metadata(
        trigger_decision={
            "decision": "retraining_recommended",
            "recommendation": "Start governed retraining.",
            "reason_count": 1,
            "reasons": [],
            "source_reports": {},
            "source_freshness": {},
        },
        training_config={"dataset": {"path": "data/churn.csv", "target_column": "churn"}},
        dataset_version={
            "dataset_name": "customer_churn",
            "version": "v1",
            "path": "data/churn.csv",
            "checksum": {"algorithm": "sha256", "value": "abc123"},
        },
        schema={
            "name": "customer_churn",
            "version": "v1",
            "target_column": "churn",
        },
        previous_production_model={
            "model_name": "customer_churn_model",
            "model_version": "v1-old",
            "artifact_uri": str(target_path),
            "status": "champion",
            "mlflow_run_id": "old-run",
            "candidate_name": "old-candidate",
            "model_type": "decision_tree",
            "dataset_name": "customer_churn",
            "dataset_version": "v1",
            "dataset_checksum": "abc123",
            "metrics": {"f1": 0.9},
            "updated_at": "2026-06-19T00:00:00+00:00",
        },
        run_id=run_id,
        created_at="2026-06-19T00:00:00+00:00",
    )
    metadata["status"] = CANDIDATE_LOCAL_SERVING_UPDATED
    metadata["candidate"].update(
        {
            "model_path": str(retraining_path),
            "model_type": "logistic_regression",
            "metrics": {"f1": 1.0},
        }
    )
    metadata["promotion"].update(
        {
            "rollback_target": {
                "model_name": "customer_churn_model",
                "model_version": "v1-old",
                "artifact_uri": str(target_path),
            },
            "local_champion_model_version": "v1-retrain-test",
            "registry_update": "completed",
            "serving_update": "local_registry_completed",
            "cloud_run_update": "not_performed",
        }
    )
    return metadata
