"""Dataset version registry loading for V3."""

import hashlib
from pathlib import Path
from typing import Any

import yaml
from yaml import YAMLError


class DatasetRegistryError(ValueError):
    """Raised when dataset version metadata is missing or invalid."""


DEFAULT_DATASET_VERSION_METADATA_PATH = Path("data_versions/customer_churn/v1.yaml")

REQUIRED_DATASET_VERSION_KEYS: tuple[str, ...] = (
    "dataset_name",
    "version",
    "path",
    "schema_path",
    "target_column",
)


def load_dataset_version_metadata(metadata_path: str | Path) -> dict[str, Any]:
    """Load and validate a dataset version metadata YAML file."""
    resolved_path = Path(metadata_path)
    if not resolved_path.exists():
        raise DatasetRegistryError(
            f"Dataset version metadata file not found: {resolved_path}"
        )

    try:
        with resolved_path.open("r", encoding="utf-8") as file:
            metadata = yaml.safe_load(file) or {}
    except OSError as exc:
        raise DatasetRegistryError(
            f"Unable to read dataset version metadata: {resolved_path}"
        ) from exc
    except YAMLError as exc:
        raise DatasetRegistryError(
            f"Invalid YAML in dataset version metadata: {resolved_path}"
        ) from exc

    if not isinstance(metadata, dict):
        raise DatasetRegistryError("Dataset version metadata root must be a dictionary.")

    validate_dataset_version_metadata(metadata)
    return metadata


def validate_dataset_version_metadata(metadata: dict[str, Any]) -> None:
    """Validate required dataset version metadata fields."""
    missing_keys = [
        key for key in REQUIRED_DATASET_VERSION_KEYS if metadata.get(key) in (None, "")
    ]
    if missing_keys:
        raise DatasetRegistryError(
            f"Missing dataset version metadata keys: {missing_keys}"
        )

    if not isinstance(metadata["dataset_name"], str):
        raise DatasetRegistryError("dataset_name must be a string.")
    if not isinstance(metadata["version"], str):
        raise DatasetRegistryError("version must be a string.")
    if not isinstance(metadata["path"], str):
        raise DatasetRegistryError("path must be a string.")
    if not isinstance(metadata["schema_path"], str):
        raise DatasetRegistryError("schema_path must be a string.")
    if not isinstance(metadata["target_column"], str):
        raise DatasetRegistryError("target_column must be a string.")


def resolve_dataset_version_metadata_path(config: dict[str, Any]) -> Path:
    """Return the dataset version metadata path from config or the project default."""
    dataset_version_config = config.get("dataset_version")
    if not isinstance(dataset_version_config, dict):
        return DEFAULT_DATASET_VERSION_METADATA_PATH

    metadata_path = dataset_version_config.get("metadata_path")
    if not metadata_path:
        return DEFAULT_DATASET_VERSION_METADATA_PATH

    return Path(str(metadata_path))


def build_dataset_version_snapshot(
    metadata_path: str | Path,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """Build the dataset version subset persisted with runtime metadata."""
    return {
        "metadata_path": str(metadata_path),
        "dataset_name": metadata["dataset_name"],
        "version": metadata["version"],
        "path": metadata["path"],
        "schema_path": metadata["schema_path"],
        "target_column": metadata["target_column"],
        "id_column": metadata.get("id_column"),
        "source_type": metadata.get("source_type"),
        "checksum": metadata.get("checksum"),
    }


def calculate_file_checksum(path: str | Path, algorithm: str = "sha256") -> str:
    """Calculate a file checksum using the requested algorithm."""
    if algorithm != "sha256":
        raise DatasetRegistryError(f"Unsupported checksum algorithm: {algorithm}")

    file_path = Path(path)
    if not file_path.exists():
        raise DatasetRegistryError(f"Dataset file not found for checksum: {file_path}")

    digest = hashlib.sha256()
    try:
        with file_path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise DatasetRegistryError(
            f"Unable to read dataset file for checksum: {file_path}"
        ) from exc

    return digest.hexdigest()


def validate_dataset_checksum(
    metadata: dict[str, Any],
    project_root: str | Path = Path("."),
) -> None:
    """Validate the dataset file checksum declared by metadata."""
    checksum = metadata.get("checksum")
    if not isinstance(checksum, dict):
        raise DatasetRegistryError("Missing dataset checksum metadata.")

    algorithm = checksum.get("algorithm")
    expected_value = checksum.get("value")
    if not isinstance(algorithm, str) or not algorithm:
        raise DatasetRegistryError("checksum.algorithm must be a string.")
    if not isinstance(expected_value, str) or not expected_value:
        raise DatasetRegistryError("checksum.value must be a string.")

    dataset_path = Path(str(metadata["path"]))
    if not dataset_path.is_absolute():
        dataset_path = Path(project_root) / dataset_path

    actual_value = calculate_file_checksum(dataset_path, algorithm)
    if actual_value.lower() != expected_value.lower():
        raise DatasetRegistryError(
            f"Dataset checksum mismatch for {dataset_path}: "
            f"expected {expected_value.lower()}, got {actual_value.lower()}"
        )
