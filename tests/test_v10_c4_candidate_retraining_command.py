import json
from pathlib import Path

from app.retraining.candidate_run_metadata import (
    APPROVAL_PENDING,
    CANDIDATE_TRAINED,
    CANDIDATE_RUN_INITIALIZED,
    build_candidate_retraining_run_metadata,
    save_candidate_retraining_run_metadata,
)
from app.retraining.candidate_training import (
    CandidateTrainingError,
    build_candidate_artifact_paths,
    run_candidate_retraining,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "lessons.md"


def test_run_candidate_retraining_persists_artifacts_and_updates_metadata(tmp_path) -> None:
    runs_dir = tmp_path / "retraining_runs"
    metadata = _candidate_metadata(run_id="retrain-test")
    save_candidate_retraining_run_metadata(metadata, runs_dir=runs_dir)

    updated_metadata, metadata_path = run_candidate_retraining(
        run_id="retrain-test",
        runs_dir=runs_dir,
        trained_at="2026-06-18T00:00:00+00:00",
    )

    candidate = updated_metadata["candidate"]
    persisted = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert updated_metadata["status"] == CANDIDATE_TRAINED
    assert persisted == updated_metadata
    assert candidate["trained_at"] == "2026-06-18T00:00:00+00:00"
    assert candidate["model_type"] == "logistic_regression"
    assert candidate["model_path"].endswith("candidate\\model.pkl") or candidate[
        "model_path"
    ].endswith("candidate/model.pkl")
    assert Path(candidate["model_path"]).is_file()
    assert Path(candidate["metrics_path"]).is_file()
    assert Path(candidate["training_metadata_path"]).is_file()
    assert "f1" in candidate["metrics"]
    assert candidate["validation"]["status"] == "passed"
    assert updated_metadata["approval"]["state"] == APPROVAL_PENDING
    assert updated_metadata["promotion"]["decision"] == APPROVAL_PENDING
    assert updated_metadata["previous_production_model"]["model_version"] == "v1-prod"


def test_run_candidate_retraining_rejects_non_initialized_run(tmp_path) -> None:
    metadata = _candidate_metadata(run_id="retrain-trained")
    metadata["status"] = CANDIDATE_TRAINED
    save_candidate_retraining_run_metadata(metadata, runs_dir=tmp_path)

    try:
        run_candidate_retraining(run_id="retrain-trained", runs_dir=tmp_path)
    except CandidateTrainingError as exc:
        assert CANDIDATE_RUN_INITIALIZED in str(exc)
    else:
        raise AssertionError("Expected CandidateTrainingError for trained run.")


def test_candidate_artifact_paths_stay_inside_retraining_run(tmp_path) -> None:
    paths = build_candidate_artifact_paths("retrain-test", runs_dir=tmp_path)

    assert paths["model"] == tmp_path / "retrain-test" / "candidate" / "model.pkl"
    assert paths["metrics"] == tmp_path / "retrain-test" / "candidate" / "metrics.json"
    assert paths["config_snapshot"] == (
        tmp_path / "retrain-test" / "candidate" / "config_snapshot.json"
    )


def test_v10_c4_docs_mention_candidate_retraining_command_and_boundary() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "python -m app.run_candidate_retraining --run-id <run_id>" in readme
    assert "V10-C4: Candidate Retraining Command" in implementation
    assert "Candidate training is still not promotion" in lessons


def _candidate_metadata(run_id: str) -> dict:
    return build_candidate_retraining_run_metadata(
        trigger_decision={
            "decision": "retraining_recommended",
            "recommendation": "Start a governed candidate retraining run.",
            "reason_count": 1,
            "reasons": [
                {
                    "name": "data_drift_detected",
                    "category": "retraining_signal",
                    "severity": "warning",
                    "source": "data_drift_summary",
                    "message": "Data drift summary detected drifted features.",
                    "recommended_action": "Start governed retraining.",
                }
            ],
            "source_reports": {
                "alerts": "reports/monitoring/alerts.json",
                "data_drift_summary": "reports/drift/data_drift_summary.json",
            },
            "source_freshness": {},
        },
        training_config={
            "dataset": {
                "path": "data/churn.csv",
                "target_column": "churn",
            }
        },
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
            "model_version": "v1-prod",
            "artifact_uri": "mlflow-run://prod/artifacts/model",
            "status": "champion",
            "mlflow_run_id": "prod",
            "candidate_name": "decision_tree_baseline",
            "model_type": "decision_tree",
            "dataset_name": "customer_churn",
            "dataset_version": "v1",
            "dataset_checksum": "abc123",
            "metrics": {"f1": 1.0},
            "updated_at": "2026-06-18T00:00:00+00:00",
        },
        run_id=run_id,
        created_at="2026-06-18T00:00:00+00:00",
        training_config_path=PROJECT_ROOT / "configs" / "training.yaml",
        dataset_version_path=PROJECT_ROOT / "data_versions" / "customer_churn" / "v1.yaml",
        schema_path=PROJECT_ROOT / "schema_versions" / "customer_churn_v1.yaml",
    )
