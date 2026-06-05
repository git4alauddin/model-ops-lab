"""Model registry metadata contract for V6."""

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_MODEL_REGISTRY_DIR = Path("model_registry")
MODEL_REGISTRY_VERSION = "v6-c2"
MODEL_LIFECYCLE_STATES = ("candidate", "champion", "archived")

REQUIRED_MODEL_VERSION_FIELDS: tuple[str, ...] = (
    "registry_version",
    "model_name",
    "model_version",
    "status",
    "created_at",
    "updated_at",
    "mlflow_run_id",
    "candidate_name",
    "model_type",
    "dataset_name",
    "dataset_version",
    "dataset_checksum",
    "metrics",
    "artifact_uri",
)


class ModelRegistryError(ValueError):
    """Raised when model registry metadata is invalid."""


def build_model_version_metadata(
    *,
    model_name: str,
    model_version: str,
    status: str,
    mlflow_run_id: str,
    candidate_name: str,
    model_type: str,
    dataset_name: str,
    dataset_version: str,
    dataset_checksum: str,
    metrics: dict[str, Any],
    artifact_uri: str,
    created_at: str | None = None,
    updated_at: str | None = None,
    promoted_from: str | None = None,
    promotion_reason: str | None = None,
    registry_version: str = MODEL_REGISTRY_VERSION,
) -> dict[str, Any]:
    """Build and validate one model registry metadata record."""
    now = datetime.now(UTC).isoformat()
    metadata = {
        "registry_version": registry_version,
        "model_name": model_name,
        "model_version": model_version,
        "status": status,
        "created_at": created_at or now,
        "updated_at": updated_at or created_at or now,
        "mlflow_run_id": mlflow_run_id,
        "candidate_name": candidate_name,
        "model_type": model_type,
        "dataset_name": dataset_name,
        "dataset_version": dataset_version,
        "dataset_checksum": dataset_checksum,
        "metrics": deepcopy(metrics),
        "artifact_uri": artifact_uri,
        "promoted_from": promoted_from,
        "promotion_reason": promotion_reason,
    }
    validate_model_version_metadata(metadata)
    return metadata


def validate_model_version_metadata(metadata: dict[str, Any]) -> None:
    """Validate the canonical V6 model version metadata contract."""
    if not isinstance(metadata, dict):
        raise ModelRegistryError("model version metadata must be a dictionary.")

    missing_fields = [
        field
        for field in REQUIRED_MODEL_VERSION_FIELDS
        if metadata.get(field) in (None, "")
    ]
    if missing_fields:
        raise ModelRegistryError(
            f"Missing model version metadata fields: {missing_fields}"
        )

    for field in REQUIRED_MODEL_VERSION_FIELDS:
        if field == "metrics":
            continue
        if not isinstance(metadata[field], str):
            raise ModelRegistryError(f"{field} must be a string.")

    status = metadata["status"]
    if status not in MODEL_LIFECYCLE_STATES:
        raise ModelRegistryError(
            "Invalid model lifecycle status: "
            f"{status}. Expected one of {list(MODEL_LIFECYCLE_STATES)}."
        )

    metrics = metadata["metrics"]
    if not isinstance(metrics, dict) or not metrics:
        raise ModelRegistryError("metrics must be a non-empty dictionary.")

    for metric_name, metric_value in metrics.items():
        if not isinstance(metric_name, str) or not metric_name:
            raise ModelRegistryError("metric names must be non-empty strings.")
        if not isinstance(metric_value, int | float):
            raise ModelRegistryError(
                f"metric value for {metric_name} must be numeric."
            )

    _validate_optional_string(metadata, "promoted_from")
    _validate_optional_string(metadata, "promotion_reason")


def _validate_optional_string(metadata: dict[str, Any], field: str) -> None:
    value = metadata.get(field)
    if value is not None and not isinstance(value, str):
        raise ModelRegistryError(f"{field} must be a string when provided.")
