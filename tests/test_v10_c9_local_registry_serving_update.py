from pathlib import Path

import joblib
import numpy as np

import app.retraining.local_serving_update as local_update
from app.model_registry import (
    build_model_version_metadata,
    find_champion_model_versions,
    get_model_versions,
    save_model_version_metadata,
)
from app.retraining.candidate_run_metadata import (
    APPROVAL_APPROVED,
    CANDIDATE_LOCAL_SERVING_UPDATED,
    CANDIDATE_SERVING_HANDOFF_VALIDATED,
    PROMOTION_DECISION_PROMOTED,
    build_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)
from app.retraining.local_serving_update import (
    LocalServingUpdateError,
    update_local_registry_and_serving,
)
from app.serving.model_loader import load_champion_model


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "lessons.md"


class DummyChurnModel:
    def predict(self, features):
        return np.ones(len(features), dtype=int)

    def predict_proba(self, features):
        return np.array([[0.2, 0.8] for _ in range(len(features))])


def test_local_serving_update_switches_champion_and_validates_prediction(tmp_path) -> None:
    runs_dir = tmp_path / "retraining_runs"
    registry_dir = tmp_path / "model_registry"
    candidate_model_path = tmp_path / "candidate" / "model.pkl"
    candidate_model_path.parent.mkdir(parents=True)
    joblib.dump(DummyChurnModel(), candidate_model_path)
    _save_previous_champion(registry_dir, tmp_path)
    metadata = _handoff_metadata(
        run_id="retrain-local",
        candidate_model_path=candidate_model_path,
    )
    save_candidate_retraining_run_metadata(metadata, runs_dir=runs_dir)

    report, updated_metadata, report_path = update_local_registry_and_serving(
        run_id="retrain-local",
        runs_dir=runs_dir,
        registry_dir=registry_dir,
        updated_at="2026-06-19T00:00:00+00:00",
    )

    champions = find_champion_model_versions(
        "customer_churn_model",
        registry_dir,
    )
    versions = get_model_versions("customer_churn_model", registry_dir)
    loaded = load_champion_model(registry_dir=registry_dir)

    assert len(champions) == 1
    assert champions[0]["model_version"] == "v1-retrain-local"
    assert champions[0]["artifact_uri"] == str(candidate_model_path)
    assert champions[0]["retraining_run_id"] == "retrain-local"
    assert any(
        version["model_version"] == "v1-old" and version["status"] == "archived"
        for version in versions
    )
    assert loaded.metadata["model_version"] == "v1-retrain-local"
    assert report["readiness_validation"]["status"] == "ready"
    assert report["prediction_validation"]["status"] == "success"
    assert report["prediction_validation"]["model_version"] == "v1-retrain-local"
    assert report["cloud_run_update"] == "not_performed"
    assert updated_metadata["status"] == CANDIDATE_LOCAL_SERVING_UPDATED
    assert updated_metadata["promotion"]["registry_update"] == "completed"
    assert (
        updated_metadata["promotion"]["serving_update"]
        == "local_registry_completed"
    )
    assert report_path.is_file()


def test_local_serving_update_requires_validated_handoff(tmp_path) -> None:
    candidate_model_path = tmp_path / "candidate.pkl"
    joblib.dump(DummyChurnModel(), candidate_model_path)
    metadata = _handoff_metadata(
        run_id="retrain-blocked",
        candidate_model_path=candidate_model_path,
    )
    metadata["status"] = "candidate_promoted"
    save_candidate_retraining_run_metadata(metadata, runs_dir=tmp_path / "runs")

    try:
        update_local_registry_and_serving(
            run_id="retrain-blocked",
            runs_dir=tmp_path / "runs",
            registry_dir=tmp_path / "registry",
        )
    except LocalServingUpdateError as exc:
        assert CANDIDATE_SERVING_HANDOFF_VALIDATED in str(exc)
    else:
        raise AssertionError("Expected LocalServingUpdateError for blocked handoff.")


def test_local_serving_update_restores_previous_champion_on_validation_failure(
    tmp_path,
    monkeypatch,
) -> None:
    runs_dir = tmp_path / "runs"
    registry_dir = tmp_path / "registry"
    candidate_model_path = tmp_path / "candidate.pkl"
    joblib.dump(DummyChurnModel(), candidate_model_path)
    _save_previous_champion(registry_dir, tmp_path)
    metadata = _handoff_metadata(
        run_id="retrain-rollback",
        candidate_model_path=candidate_model_path,
    )
    save_candidate_retraining_run_metadata(metadata, runs_dir=runs_dir)

    def fail_validation(**kwargs):
        raise LocalServingUpdateError("simulated serving validation failure")

    monkeypatch.setattr(local_update, "_validate_updated_serving", fail_validation)

    try:
        update_local_registry_and_serving(
            run_id="retrain-rollback",
            runs_dir=runs_dir,
            registry_dir=registry_dir,
        )
    except LocalServingUpdateError as exc:
        assert "simulated serving validation failure" in str(exc)
    else:
        raise AssertionError("Expected LocalServingUpdateError.")

    champions = find_champion_model_versions(
        "customer_churn_model",
        registry_dir,
    )
    versions = get_model_versions("customer_churn_model", registry_dir)

    assert len(champions) == 1
    assert champions[0]["model_version"] == "v1-old"
    assert all(version["model_version"] != "v1-retrain-rollback" for version in versions)


def test_local_serving_update_rejects_duplicate_registry_version(tmp_path) -> None:
    runs_dir = tmp_path / "runs"
    registry_dir = tmp_path / "registry"
    candidate_model_path = tmp_path / "candidate.pkl"
    joblib.dump(DummyChurnModel(), candidate_model_path)
    _save_previous_champion(registry_dir, tmp_path)
    duplicate = build_model_version_metadata(
        model_name="customer_churn_model",
        model_version="v1-retrain-duplicate",
        status="archived",
        mlflow_run_id="existing-run",
        candidate_name="existing",
        model_type="logistic_regression",
        dataset_name="customer_churn",
        dataset_version="v1",
        dataset_checksum="abc123",
        metrics={"f1": 0.8},
        artifact_uri=str(candidate_model_path),
    )
    save_model_version_metadata(duplicate, output_dir=registry_dir)
    metadata = _handoff_metadata(
        run_id="retrain-duplicate",
        candidate_model_path=candidate_model_path,
    )
    save_candidate_retraining_run_metadata(metadata, runs_dir=runs_dir)

    try:
        update_local_registry_and_serving(
            run_id="retrain-duplicate",
            runs_dir=runs_dir,
            registry_dir=registry_dir,
        )
    except LocalServingUpdateError as exc:
        assert "Target registry version already exists" in str(exc)
    else:
        raise AssertionError("Expected duplicate registry version failure.")


def test_v10_c9_docs_mention_local_serving_update_and_cloud_boundary() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "python -m app.update_local_serving_model --run-id <run_id>" in readme
    assert "retraining_runs/<run_id>/local_serving_update_report.json" in readme
    assert "V10-C9: Local Registry and Serving Update" in implementation
    assert "Local serving update is a real production-state mutation" in lessons
    assert "Cloud Run remains unchanged" in lessons


def _save_previous_champion(registry_dir: Path, tmp_path: Path) -> None:
    old_model_path = tmp_path / "old-model.pkl"
    joblib.dump(DummyChurnModel(), old_model_path)
    metadata = build_model_version_metadata(
        model_name="customer_churn_model",
        model_version="v1-old",
        status="champion",
        mlflow_run_id="old-run",
        candidate_name="old-candidate",
        model_type="decision_tree",
        dataset_name="customer_churn",
        dataset_version="v1",
        dataset_checksum="abc123",
        metrics={"f1": 0.9},
        artifact_uri=str(old_model_path),
    )
    save_model_version_metadata(metadata, output_dir=registry_dir)


def _handoff_metadata(
    *,
    run_id: str,
    candidate_model_path: Path,
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
            "artifact_uri": "old-model.pkl",
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
    metadata["status"] = CANDIDATE_SERVING_HANDOFF_VALIDATED
    metadata["candidate"].update(
        {
            "model_path": str(candidate_model_path),
            "metrics_path": str(candidate_model_path.with_name("metrics.json")),
            "comparison_report_path": "comparison_report.json",
            "model_type": "logistic_regression",
            "metrics": {
                "accuracy": 1.0,
                "precision": 1.0,
                "recall": 1.0,
                "f1": 1.0,
            },
        }
    )
    metadata["approval"] = {
        "state": APPROVAL_APPROVED,
        "approved_by": "alauddin",
        "approved_at": "2026-06-19T00:00:00+00:00",
        "notes": "Approved.",
    }
    metadata["promotion"].update(
        {
            "decision": PROMOTION_DECISION_PROMOTED,
            "reason": "Approved candidate.",
            "serving_handoff_status": "ready",
            "serving_update_ready": True,
            "registry_update": "not_performed",
            "serving_update": "not_performed",
        }
    )
    return metadata
