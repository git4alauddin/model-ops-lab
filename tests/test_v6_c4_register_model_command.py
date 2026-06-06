"""Tests for V6 model registration command."""

import json

from app.model_registry import load_model_version_metadata
from app.register_model import (
    ModelRegistrationError,
    register_champion_model,
)


def _champion_report() -> dict:
    return {
        "generated_at": "2026-06-06T10:00:00+00:00",
        "selection_rule": "highest_f1",
        "primary_metric": "f1",
        "champion": {
            "run_id": "run123456789",
            "candidate_name": "decision_tree_baseline",
            "model_type": "decision_tree",
            "dataset_name": "customer_churn",
            "dataset_version": "v1",
            "dataset_checksum": "abc123",
            "metrics": {
                "accuracy": 0.91,
                "precision": 0.88,
                "recall": 0.86,
                "f1": 0.87,
                "training_duration_seconds": 0.2,
                "evaluation_duration_seconds": 0.1,
            },
            "selection_reason": "Selected by highest F1.",
        },
        "eligible_runs": [],
        "rejected_runs": [],
    }


def test_register_champion_model_persists_candidate_record(tmp_path):
    champion_report_path = tmp_path / "champion_run.json"
    champion_report_path.write_text(
        json.dumps(_champion_report()),
        encoding="utf-8",
    )

    metadata = register_champion_model(
        champion_report_path,
        output_dir=tmp_path / "model_registry",
    )

    assert metadata["model_name"] == "customer_churn_model"
    assert metadata["model_version"] == "v1-run12345"
    assert metadata["status"] == "candidate"
    assert metadata["mlflow_run_id"] == "run123456789"
    assert metadata["artifact_uri"] == "mlflow-run://run123456789/artifacts/model"

    loaded_metadata = load_model_version_metadata(
        "customer_churn_model",
        "v1-run12345",
        output_dir=tmp_path / "model_registry",
    )
    assert loaded_metadata == metadata


def test_register_champion_model_accepts_explicit_model_version(tmp_path):
    champion_report_path = tmp_path / "champion_run.json"
    champion_report_path.write_text(
        json.dumps(_champion_report()),
        encoding="utf-8",
    )

    metadata = register_champion_model(
        champion_report_path,
        model_version="manual-v1",
        output_dir=tmp_path / "model_registry",
    )

    assert metadata["model_version"] == "manual-v1"


def test_register_champion_model_fails_when_report_is_missing(tmp_path):
    missing_report_path = tmp_path / "missing_champion_run.json"

    try:
        register_champion_model(
            missing_report_path,
            output_dir=tmp_path / "model_registry",
        )
    except ModelRegistrationError as exc:
        assert "Champion report not found" in str(exc)
    else:
        raise AssertionError("Expected ModelRegistrationError for missing report.")


def test_register_champion_model_fails_when_champion_is_missing(tmp_path):
    champion_report_path = tmp_path / "champion_run.json"
    champion_report_path.write_text(json.dumps({"eligible_runs": []}), encoding="utf-8")

    try:
        register_champion_model(
            champion_report_path,
            output_dir=tmp_path / "model_registry",
        )
    except ModelRegistrationError as exc:
        assert "requires a champion object" in str(exc)
    else:
        raise AssertionError("Expected ModelRegistrationError for missing champion.")


def test_register_champion_model_fails_when_champion_field_is_missing(tmp_path):
    report = _champion_report()
    report["champion"].pop("dataset_checksum")
    champion_report_path = tmp_path / "champion_run.json"
    champion_report_path.write_text(json.dumps(report), encoding="utf-8")

    try:
        register_champion_model(
            champion_report_path,
            output_dir=tmp_path / "model_registry",
        )
    except ModelRegistrationError as exc:
        assert "dataset_checksum" in str(exc)
    else:
        raise AssertionError("Expected ModelRegistrationError for incomplete report.")
