import json
from pathlib import Path

import pytest
import yaml

from app.model_registry import build_model_version_metadata, save_model_version_metadata
from app.observability.retraining_trigger import (
    RETRAINING_NOT_REQUIRED,
    RETRAINING_RECOMMENDED,
)
from app.retraining.candidate_run_metadata import (
    APPROVAL_PENDING,
    CANDIDATE_RUN_INITIALIZED,
    CandidateRetrainingRunError,
    build_and_save_candidate_retraining_run_metadata,
    build_candidate_retraining_run_metadata,
    find_previous_production_model,
    load_json_object,
    load_yaml_object,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "lessons.md"


def test_candidate_retraining_metadata_initializes_governed_run() -> None:
    previous_model = _previous_production_model()

    metadata = build_candidate_retraining_run_metadata(
        trigger_decision=_trigger_decision(),
        training_config=_training_config(),
        dataset_version=_dataset_version(),
        schema=_schema(),
        previous_production_model=previous_model,
        run_id="retrain-test",
        created_at="2026-06-17T00:00:00+00:00",
    )

    assert metadata["run_id"] == "retrain-test"
    assert metadata["status"] == CANDIDATE_RUN_INITIALIZED
    assert metadata["approval"]["state"] == APPROVAL_PENDING
    assert metadata["promotion"]["decision"] == APPROVAL_PENDING
    assert metadata["trigger"]["decision"] == RETRAINING_RECOMMENDED
    assert metadata["lineage"]["dataset_name"] == "customer_churn"
    assert metadata["lineage"]["dataset_version"] == "v1"
    assert metadata["lineage"]["schema_version"] == "v1"
    assert metadata["previous_production_model"]["model_version"] == "v1-prod"
    assert metadata["promotion"]["rollback_target"] == {
        "model_name": "customer_churn_model",
        "model_version": "v1-prod",
        "artifact_uri": "mlflow-run://prod/artifacts/model",
    }
    assert metadata["candidate"]["model_path"] is None
    assert metadata["regression_gates"]["status"] == "not_evaluated"


def test_candidate_retraining_metadata_rejects_non_recommended_trigger() -> None:
    trigger_decision = _trigger_decision(decision=RETRAINING_NOT_REQUIRED)

    with pytest.raises(CandidateRetrainingRunError, match="requires decision"):
        build_candidate_retraining_run_metadata(
            trigger_decision=trigger_decision,
            training_config=_training_config(),
            dataset_version=_dataset_version(),
            schema=_schema(),
            previous_production_model=_previous_production_model(),
        )


def test_build_and_save_candidate_retraining_metadata_persists_json(tmp_path) -> None:
    trigger_path = tmp_path / "retraining_trigger_decision.json"
    config_path = tmp_path / "training.yaml"
    dataset_version_path = tmp_path / "v1.yaml"
    schema_path = tmp_path / "customer_churn_v1.yaml"
    registry_dir = tmp_path / "model_registry"
    runs_dir = tmp_path / "retraining_runs"
    trigger_path.write_text(json.dumps(_trigger_decision()), encoding="utf-8")
    config_path.write_text(yaml.safe_dump(_training_config()), encoding="utf-8")
    dataset_version_path.write_text(yaml.safe_dump(_dataset_version()), encoding="utf-8")
    schema_path.write_text(yaml.safe_dump(_schema()), encoding="utf-8")
    save_model_version_metadata(_registry_champion(), output_dir=registry_dir)

    metadata, output_path = build_and_save_candidate_retraining_run_metadata(
        trigger_decision_path=trigger_path,
        training_config_path=config_path,
        dataset_version_path=dataset_version_path,
        schema_path=schema_path,
        runs_dir=runs_dir,
        registry_dir=registry_dir,
        run_id="retrain-test",
        created_at="2026-06-17T00:00:00+00:00",
    )

    persisted = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path == runs_dir / "retrain-test" / "retraining_metadata.json"
    assert persisted == metadata
    assert persisted["previous_production_model"]["model_version"] == "v1-prod"


def test_find_previous_production_model_handles_missing_and_multiple_champions(tmp_path) -> None:
    assert find_previous_production_model(registry_dir=tmp_path) is None

    save_model_version_metadata(
        _registry_champion(model_version="v1-prod"),
        output_dir=tmp_path,
    )
    save_model_version_metadata(
        _registry_champion(model_version="v2-prod", mlflow_run_id="run-2"),
        output_dir=tmp_path,
    )

    with pytest.raises(CandidateRetrainingRunError, match="Expected one production champion"):
        find_previous_production_model(registry_dir=tmp_path)


def test_candidate_retraining_source_loaders_reject_missing_or_invalid_files(tmp_path) -> None:
    with pytest.raises(CandidateRetrainingRunError, match="not found"):
        load_json_object(tmp_path / "missing.json")
    with pytest.raises(CandidateRetrainingRunError, match="not found"):
        load_yaml_object(tmp_path / "missing.yaml")

    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{not-json", encoding="utf-8")
    with pytest.raises(CandidateRetrainingRunError, match="Invalid JSON"):
        load_json_object(invalid_json)

    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text("name: [", encoding="utf-8")
    with pytest.raises(CandidateRetrainingRunError, match="Invalid YAML"):
        load_yaml_object(invalid_yaml)


def test_v10_c3_docs_mention_candidate_run_command_and_metadata() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "python -m app.start_candidate_retraining_run" in readme
    assert "retraining_runs/<run_id>/retraining_metadata.json" in readme
    assert "V10-C3: Candidate Retraining Run Metadata" in implementation
    assert "Candidate run metadata is the handoff" in lessons


def _trigger_decision(decision: str = RETRAINING_RECOMMENDED) -> dict:
    return {
        "generated_at": "2026-06-17T00:00:00+00:00",
        "decision": decision,
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
        "source_freshness": {
            "alerts_generated_at": "2026-06-17T00:00:00+00:00",
            "data_drift_summary_generated_at": "2026-06-17T00:00:00+00:00",
        },
    }


def _training_config() -> dict:
    return {
        "dataset": {
            "path": "data/churn.csv",
            "target_column": "churn",
        }
    }


def _dataset_version() -> dict:
    return {
        "dataset_name": "customer_churn",
        "version": "v1",
        "path": "data/churn.csv",
        "checksum": {
            "algorithm": "sha256",
            "value": "abc123",
        },
    }


def _schema() -> dict:
    return {
        "name": "customer_churn",
        "version": "v1",
        "target_column": "churn",
    }


def _previous_production_model() -> dict:
    return {
        "model_name": "customer_churn_model",
        "model_version": "v1-prod",
        "status": "champion",
        "mlflow_run_id": "prod",
        "candidate_name": "decision_tree_baseline",
        "model_type": "decision_tree",
        "dataset_name": "customer_churn",
        "dataset_version": "v1",
        "dataset_checksum": "abc123",
        "metrics": {"f1": 1.0},
        "artifact_uri": "mlflow-run://prod/artifacts/model",
        "updated_at": "2026-06-17T00:00:00+00:00",
    }


def _registry_champion(
    *,
    model_version: str = "v1-prod",
    mlflow_run_id: str = "prod",
) -> dict:
    return build_model_version_metadata(
        model_name="customer_churn_model",
        model_version=model_version,
        status="champion",
        mlflow_run_id=mlflow_run_id,
        candidate_name="decision_tree_baseline",
        model_type="decision_tree",
        dataset_name="customer_churn",
        dataset_version="v1",
        dataset_checksum="abc123",
        metrics={"f1": 1.0},
        artifact_uri=f"mlflow-run://{mlflow_run_id}/artifacts/model",
        created_at="2026-06-17T00:00:00+00:00",
        updated_at="2026-06-17T00:00:00+00:00",
    )
