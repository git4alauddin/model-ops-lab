"""Tests for V6 model registry metadata contract."""

from app.model_registry import (
    MODEL_LIFECYCLE_STATES,
    MODEL_REGISTRY_VERSION,
    ModelRegistryError,
    build_model_version_metadata,
    validate_model_version_metadata,
)


def _valid_model_metadata(status: str = "candidate") -> dict:
    return build_model_version_metadata(
        model_name="customer_churn_model",
        model_version="v1",
        status=status,
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


def test_build_model_version_metadata_uses_expected_contract():
    metadata = _valid_model_metadata()

    assert metadata == {
        "registry_version": MODEL_REGISTRY_VERSION,
        "model_name": "customer_churn_model",
        "model_version": "v1",
        "status": "candidate",
        "created_at": "2026-06-06T10:00:00+00:00",
        "updated_at": "2026-06-06T10:00:00+00:00",
        "mlflow_run_id": "mlflow-run-001",
        "candidate_name": "logistic_regression",
        "model_type": "LogisticRegression",
        "dataset_name": "customer_churn",
        "dataset_version": "v1",
        "dataset_checksum": "abc123",
        "metrics": {"accuracy": 0.91, "f1": 0.84},
        "artifact_uri": "mlruns/1/mlflow-run-001/artifacts/model",
        "promoted_from": None,
        "promotion_reason": None,
    }


def test_validate_model_version_metadata_rejects_missing_required_field():
    metadata = _valid_model_metadata()
    metadata.pop("mlflow_run_id")

    try:
        validate_model_version_metadata(metadata)
    except ModelRegistryError as exc:
        assert "mlflow_run_id" in str(exc)
    else:
        raise AssertionError("Expected ModelRegistryError for missing mlflow_run_id.")


def test_validate_model_version_metadata_rejects_invalid_lifecycle_state():
    try:
        _valid_model_metadata(status="production")
    except ModelRegistryError as exc:
        assert "Invalid model lifecycle status" in str(exc)
    else:
        raise AssertionError("Expected ModelRegistryError for invalid lifecycle state.")


def test_validate_model_version_metadata_supports_all_lifecycle_states():
    assert MODEL_LIFECYCLE_STATES == ("candidate", "champion", "archived")

    for status in MODEL_LIFECYCLE_STATES:
        metadata = _valid_model_metadata(status=status)

        assert metadata["status"] == status


def test_validate_model_version_metadata_rejects_non_numeric_metric():
    metadata = _valid_model_metadata()
    metadata["metrics"]["f1"] = "0.84"

    try:
        validate_model_version_metadata(metadata)
    except ModelRegistryError as exc:
        assert "metric value for f1 must be numeric" in str(exc)
    else:
        raise AssertionError("Expected ModelRegistryError for invalid metric value.")
