"""Tests for V3 dataset registry foundation."""

from pathlib import Path

from app.dataset_registry import (
    DatasetRegistryError,
    load_dataset_version_metadata,
    validate_dataset_version_metadata,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_load_dataset_version_metadata_success():
    metadata = load_dataset_version_metadata(
        PROJECT_ROOT / "data_versions" / "customer_churn" / "v1.yaml"
    )

    assert metadata["dataset_name"] == "customer_churn"
    assert metadata["version"] == "v1"
    assert metadata["path"] == "data/churn.csv"
    assert metadata["schema_path"] == "schema_versions/customer_churn_v1.yaml"


def test_load_dataset_version_metadata_missing_file(tmp_path):
    missing_file = tmp_path / "missing.yaml"

    try:
        load_dataset_version_metadata(missing_file)
    except DatasetRegistryError as exc:
        assert "metadata file not found" in str(exc)
    else:
        raise AssertionError("Expected DatasetRegistryError for missing metadata file.")


def test_load_dataset_version_metadata_rejects_invalid_yaml(tmp_path):
    metadata_file = tmp_path / "dataset.yaml"
    metadata_file.write_text("dataset_name: [", encoding="utf-8")

    try:
        load_dataset_version_metadata(metadata_file)
    except DatasetRegistryError as exc:
        assert "Invalid YAML" in str(exc)
    else:
        raise AssertionError("Expected DatasetRegistryError for invalid YAML.")


def test_validate_dataset_version_metadata_requires_core_fields():
    metadata = {
        "dataset_name": "customer_churn",
        "version": "v1",
        "path": "data/churn.csv",
        "target_column": "churn",
    }

    try:
        validate_dataset_version_metadata(metadata)
    except DatasetRegistryError as exc:
        assert "schema_path" in str(exc)
    else:
        raise AssertionError("Expected DatasetRegistryError for missing schema_path.")


def test_validate_dataset_version_metadata_requires_string_values():
    metadata = {
        "dataset_name": "customer_churn",
        "version": 1,
        "path": "data/churn.csv",
        "schema_path": "schema_versions/customer_churn_v1.yaml",
        "target_column": "churn",
    }

    try:
        validate_dataset_version_metadata(metadata)
    except DatasetRegistryError as exc:
        assert "version must be a string" in str(exc)
    else:
        raise AssertionError("Expected DatasetRegistryError for non-string version.")
