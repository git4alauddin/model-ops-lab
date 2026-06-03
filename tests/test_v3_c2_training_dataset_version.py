"""Tests for V3 training dataset version metadata."""

from pathlib import Path

from app.dataset_registry import (
    DatasetRegistryError,
    build_dataset_version_snapshot,
    load_dataset_version_metadata,
    resolve_dataset_version_metadata_path,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_resolve_dataset_version_metadata_path_from_config():
    path = resolve_dataset_version_metadata_path(
        {"dataset_version": {"metadata_path": "data_versions/customer_churn/v1.yaml"}}
    )

    assert path == Path("data_versions/customer_churn/v1.yaml")


def test_resolve_dataset_version_metadata_path_default():
    path = resolve_dataset_version_metadata_path({})

    assert path == Path("data_versions/customer_churn/v1.yaml")


def test_build_dataset_version_snapshot_for_training_metadata():
    metadata_path = PROJECT_ROOT / "data_versions" / "customer_churn" / "v1.yaml"
    metadata = load_dataset_version_metadata(metadata_path)

    snapshot = build_dataset_version_snapshot(metadata_path, metadata)

    assert snapshot["metadata_path"] == str(metadata_path)
    assert snapshot["dataset_name"] == "customer_churn"
    assert snapshot["version"] == "v1"
    assert snapshot["path"] == "data/churn.csv"
    assert snapshot["schema_path"] == "schema_versions/customer_churn_v1.yaml"
    assert snapshot["target_column"] == "churn"
    assert snapshot["id_column"] == "customer_id"
    assert snapshot["source_type"] == "local_csv"
    assert snapshot["checksum"]["algorithm"] == "sha256"
    assert snapshot["checksum"]["value"] == (
        "5f4f99466d4ef2703be65c8597a6bd0d784eaaf83960690bdac118ff3cfae623"
    )


def test_configured_missing_dataset_version_metadata_fails_safely(tmp_path):
    missing_metadata = tmp_path / "missing.yaml"
    path = resolve_dataset_version_metadata_path(
        {"dataset_version": {"metadata_path": str(missing_metadata)}}
    )

    try:
        load_dataset_version_metadata(path)
    except DatasetRegistryError as exc:
        assert "metadata file not found" in str(exc)
    else:
        raise AssertionError("Expected DatasetRegistryError for missing metadata file.")
