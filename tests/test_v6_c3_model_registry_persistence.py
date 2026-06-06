"""Tests for V6 model registry persistence."""

import json

from app.model_registry import (
    ModelRegistryError,
    build_model_version_metadata,
    build_model_version_metadata_path,
    load_model_version_metadata,
    save_model_version_metadata,
)


def _valid_model_metadata() -> dict:
    return build_model_version_metadata(
        model_name="customer_churn_model",
        model_version="v1",
        status="candidate",
        created_at="2026-06-06T10:00:00+00:00",
        updated_at="2026-06-06T10:00:00+00:00",
        mlflow_run_id="mlflow-run-001",
        candidate_name="logistic_regression",
        model_type="LogisticRegression",
        dataset_name="customer_churn",
        dataset_version="v1",
        dataset_checksum="abc123",
        metrics={"accuracy": 0.91, "f1": 0.84},
        artifact_uri="mlruns/1/mlflow-run-001/artifacts/model",
    )


def test_build_model_version_metadata_path_uses_safe_filename(tmp_path):
    path = build_model_version_metadata_path(
        "customer_churn_model",
        "v1",
        output_dir=tmp_path,
    )

    assert path == tmp_path / "customer_churn_model__v1.json"


def test_save_model_version_metadata_persists_json(tmp_path):
    metadata = _valid_model_metadata()

    output_path = save_model_version_metadata(metadata, output_dir=tmp_path)

    assert output_path == tmp_path / "customer_churn_model__v1.json"
    assert json.loads(output_path.read_text(encoding="utf-8")) == metadata


def test_load_model_version_metadata_returns_validated_metadata(tmp_path):
    metadata = _valid_model_metadata()
    save_model_version_metadata(metadata, output_dir=tmp_path)

    loaded_metadata = load_model_version_metadata(
        "customer_churn_model",
        "v1",
        output_dir=tmp_path,
    )

    assert loaded_metadata == metadata


def test_build_model_version_metadata_path_rejects_unsafe_model_name(tmp_path):
    try:
        build_model_version_metadata_path("../bad", "v1", output_dir=tmp_path)
    except ModelRegistryError as exc:
        assert "model_name must be filesystem-safe" in str(exc)
    else:
        raise AssertionError("Expected ModelRegistryError for unsafe model name.")


def test_build_model_version_metadata_path_rejects_unsafe_model_version(tmp_path):
    try:
        build_model_version_metadata_path(
            "customer_churn_model",
            "../v1",
            output_dir=tmp_path,
        )
    except ModelRegistryError as exc:
        assert "model_version must be filesystem-safe" in str(exc)
    else:
        raise AssertionError("Expected ModelRegistryError for unsafe model version.")


def test_load_model_version_metadata_rejects_invalid_loaded_metadata(tmp_path):
    metadata = _valid_model_metadata()
    metadata.pop("mlflow_run_id")
    path = tmp_path / "customer_churn_model__v1.json"
    path.write_text(json.dumps(metadata), encoding="utf-8")

    try:
        load_model_version_metadata("customer_churn_model", "v1", output_dir=tmp_path)
    except ModelRegistryError as exc:
        assert "mlflow_run_id" in str(exc)
    else:
        raise AssertionError("Expected ModelRegistryError for invalid loaded metadata.")
