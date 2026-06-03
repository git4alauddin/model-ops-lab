"""Tests for V3 dataset checksum tracking."""

from pathlib import Path

from app.dataset_registry import (
    DatasetRegistryError,
    calculate_file_checksum,
    load_dataset_version_metadata,
    validate_dataset_checksum,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CHURN_SHA256 = (
    "5f4f99466d4ef2703be65c8597a6bd0d784eaaf83960690bdac118ff3cfae623"
)


def test_calculate_file_checksum_is_deterministic():
    dataset_path = PROJECT_ROOT / "data" / "churn.csv"

    first_checksum = calculate_file_checksum(dataset_path)
    second_checksum = calculate_file_checksum(dataset_path)

    assert first_checksum == EXPECTED_CHURN_SHA256
    assert second_checksum == EXPECTED_CHURN_SHA256


def test_validate_dataset_checksum_accepts_current_dataset_version():
    metadata = load_dataset_version_metadata(
        PROJECT_ROOT / "data_versions" / "customer_churn" / "v1.yaml"
    )

    validate_dataset_checksum(metadata, PROJECT_ROOT)


def test_validate_dataset_checksum_rejects_mismatch():
    metadata = load_dataset_version_metadata(
        PROJECT_ROOT / "data_versions" / "customer_churn" / "v1.yaml"
    )
    metadata["checksum"] = {
        "algorithm": "sha256",
        "value": "0" * 64,
    }

    try:
        validate_dataset_checksum(metadata, PROJECT_ROOT)
    except DatasetRegistryError as exc:
        assert "checksum mismatch" in str(exc)
    else:
        raise AssertionError("Expected DatasetRegistryError for checksum mismatch.")


def test_validate_dataset_checksum_rejects_missing_dataset_file(tmp_path):
    metadata = load_dataset_version_metadata(
        PROJECT_ROOT / "data_versions" / "customer_churn" / "v1.yaml"
    )
    metadata["path"] = "missing.csv"

    try:
        validate_dataset_checksum(metadata, tmp_path)
    except DatasetRegistryError as exc:
        assert "Dataset file not found for checksum" in str(exc)
    else:
        raise AssertionError("Expected DatasetRegistryError for missing dataset file.")


def test_validate_dataset_checksum_rejects_unsupported_algorithm():
    metadata = load_dataset_version_metadata(
        PROJECT_ROOT / "data_versions" / "customer_churn" / "v1.yaml"
    )
    metadata["checksum"] = {
        "algorithm": "md5",
        "value": "unused",
    }

    try:
        validate_dataset_checksum(metadata, PROJECT_ROOT)
    except DatasetRegistryError as exc:
        assert "Unsupported checksum algorithm" in str(exc)
    else:
        raise AssertionError("Expected DatasetRegistryError for unsupported checksum.")
