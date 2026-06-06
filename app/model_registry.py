"""Model registry metadata contract for V6."""

from copy import deepcopy
from datetime import UTC, datetime
import json
from pathlib import Path
import re
from typing import Any

from app.utils.artifacts import ArtifactError, save_json

DEFAULT_MODEL_REGISTRY_DIR = Path("model_registry")
MODEL_REGISTRY_VERSION = "v6-c2"
MODEL_LIFECYCLE_STATES = ("candidate", "champion", "archived")
_SAFE_MODEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")

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


def build_model_version_metadata_path(
    model_name: str,
    model_version: str,
    output_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> Path:
    """Build a safe registry metadata JSON path for one model version."""
    _validate_safe_model_identifier(model_name, "model_name")
    _validate_safe_model_identifier(model_version, "model_version")
    return output_dir / f"{model_name}__{model_version}.json"


def save_model_version_metadata(
    metadata: dict[str, Any],
    output_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> Path:
    """Validate and persist one model registry metadata record."""
    validate_model_version_metadata(metadata)
    path = build_model_version_metadata_path(
        metadata["model_name"],
        metadata["model_version"],
        output_dir,
    )
    try:
        save_json(metadata, path)
    except ArtifactError as exc:
        raise ModelRegistryError("Failed to save model registry metadata.") from exc
    return path


def load_model_version_metadata(
    model_name: str,
    model_version: str,
    output_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> dict[str, Any]:
    """Load and validate one model registry metadata record."""
    path = build_model_version_metadata_path(model_name, model_version, output_dir)
    try:
        with path.open("r", encoding="utf-8") as file:
            metadata = json.load(file)
    except FileNotFoundError as exc:
        raise ModelRegistryError(
            f"Model registry metadata file not found: {path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ModelRegistryError(
            f"Invalid JSON in model registry metadata: {path}"
        ) from exc
    except OSError as exc:
        raise ModelRegistryError(
            f"Unable to read model registry metadata: {path}"
        ) from exc

    validate_model_version_metadata(metadata)
    return metadata


def list_model_version_metadata(
    output_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> list[dict[str, Any]]:
    """Load and validate all model registry metadata records."""
    registry_dir = Path(output_dir)
    if not registry_dir.exists():
        return []

    records = []
    for metadata_path in sorted(registry_dir.glob("*__*.json")):
        try:
            with metadata_path.open("r", encoding="utf-8") as file:
                metadata = json.load(file)
        except json.JSONDecodeError as exc:
            raise ModelRegistryError(
                f"Invalid JSON in model registry metadata: {metadata_path}"
            ) from exc
        except OSError as exc:
            raise ModelRegistryError(
                f"Unable to read model registry metadata: {metadata_path}"
            ) from exc

        validate_model_version_metadata(metadata)
        records.append(metadata)
    return records


def find_champion_model_versions(
    model_name: str,
    output_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> list[dict[str, Any]]:
    """Return champion records for one model name."""
    _validate_safe_model_identifier(model_name, "model_name")
    return [
        metadata
        for metadata in list_model_version_metadata(output_dir)
        if metadata["model_name"] == model_name and metadata["status"] == "champion"
    ]


def get_model_versions(
    model_name: str,
    output_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> list[dict[str, Any]]:
    """Return registry records for one model name."""
    _validate_safe_model_identifier(model_name, "model_name")
    return [
        metadata
        for metadata in list_model_version_metadata(output_dir)
        if metadata["model_name"] == model_name
    ]


def archive_existing_champions(
    model_name: str,
    *,
    exclude_model_version: str | None = None,
    archive_reason: str = "Archived by new champion promotion.",
    output_dir: Path = DEFAULT_MODEL_REGISTRY_DIR,
) -> list[dict[str, Any]]:
    """Archive current champions for a model, optionally excluding one version."""
    archived_records = []
    for champion in find_champion_model_versions(model_name, output_dir):
        if champion["model_version"] == exclude_model_version:
            continue
        archived_metadata = update_model_lifecycle_status(
            champion,
            status="archived",
            promotion_reason=archive_reason,
        )
        save_model_version_metadata(archived_metadata, output_dir=output_dir)
        archived_records.append(archived_metadata)
    return archived_records


def update_model_lifecycle_status(
    metadata: dict[str, Any],
    *,
    status: str,
    promotion_reason: str | None = None,
    updated_at: str | None = None,
) -> dict[str, Any]:
    """Return validated metadata with an updated lifecycle status."""
    validate_model_version_metadata(metadata)
    if status not in MODEL_LIFECYCLE_STATES:
        raise ModelRegistryError(
            "Invalid model lifecycle status: "
            f"{status}. Expected one of {list(MODEL_LIFECYCLE_STATES)}."
        )

    previous_status = metadata["status"]
    updated_metadata = deepcopy(metadata)
    updated_metadata["status"] = status
    updated_metadata["updated_at"] = updated_at or datetime.now(UTC).isoformat()
    updated_metadata["promoted_from"] = previous_status
    if promotion_reason is not None:
        updated_metadata["promotion_reason"] = promotion_reason

    validate_model_version_metadata(updated_metadata)
    return updated_metadata


def _validate_optional_string(metadata: dict[str, Any], field: str) -> None:
    value = metadata.get(field)
    if value is not None and not isinstance(value, str):
        raise ModelRegistryError(f"{field} must be a string when provided.")


def _validate_safe_model_identifier(value: str, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise ModelRegistryError(f"{field} must be a non-empty string.")
    if not _SAFE_MODEL_ID_PATTERN.fullmatch(value):
        raise ModelRegistryError(f"{field} must be filesystem-safe.")
