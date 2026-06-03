"""Tests for V3 reproducibility check command."""

from pathlib import Path

from app.check_reproducibility import check_reproducibility
from app.dataset_registry import DatasetRegistryError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CHURN_SHA256 = (
    "5f4f99466d4ef2703be65c8597a6bd0d784eaaf83960690bdac118ff3cfae623"
)


def test_check_reproducibility_passes_for_current_dataset():
    result = check_reproducibility(PROJECT_ROOT / "configs" / "training.yaml")

    assert result.status == "passed"
    assert result.dataset_name == "customer_churn"
    assert result.version == "v1"
    assert result.checksum_algorithm == "sha256"
    assert result.expected_checksum == EXPECTED_CHURN_SHA256
    assert result.actual_checksum == EXPECTED_CHURN_SHA256


def test_check_reproducibility_rejects_checksum_mismatch(tmp_path):
    dataset_file = tmp_path / "dataset.csv"
    dataset_file.write_text("id,value\n1,a\n", encoding="utf-8")
    metadata_file = tmp_path / "metadata.yaml"
    metadata_file.write_text(
        "\n".join(
            [
                "dataset_name: fixture",
                "version: v1",
                "path: dataset.csv",
                "schema_path: schema.yaml",
                "target_column: value",
                "checksum:",
                "  algorithm: sha256",
                f"  value: '{'0' * 64}'",
            ]
        ),
        encoding="utf-8",
    )
    config_file = _write_config(tmp_path, metadata_file)

    try:
        check_reproducibility(config_file)
    except DatasetRegistryError as exc:
        assert "checksum mismatch" in str(exc)
    else:
        raise AssertionError("Expected DatasetRegistryError for checksum mismatch.")


def test_check_reproducibility_rejects_missing_dataset_file(tmp_path):
    metadata_file = tmp_path / "metadata.yaml"
    metadata_file.write_text(
        "\n".join(
            [
                "dataset_name: fixture",
                "version: v1",
                "path: missing.csv",
                "schema_path: schema.yaml",
                "target_column: value",
                "checksum:",
                "  algorithm: sha256",
                f"  value: {EXPECTED_CHURN_SHA256}",
            ]
        ),
        encoding="utf-8",
    )
    config_file = _write_config(tmp_path, metadata_file)

    try:
        check_reproducibility(config_file)
    except DatasetRegistryError as exc:
        assert "Dataset file not found for checksum" in str(exc)
    else:
        raise AssertionError("Expected DatasetRegistryError for missing dataset file.")


def test_check_reproducibility_rejects_missing_registry_file(tmp_path):
    config_file = _write_config(tmp_path, tmp_path / "missing.yaml")

    try:
        check_reproducibility(config_file)
    except DatasetRegistryError as exc:
        assert "metadata file not found" in str(exc)
    else:
        raise AssertionError("Expected DatasetRegistryError for missing metadata file.")


def _write_config(tmp_path: Path, metadata_file: Path) -> Path:
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    config_file = config_dir / "training.yaml"
    config_file.write_text(
        "\n".join(
            [
                "dataset:",
                "  path: dataset.csv",
                "  target_column: value",
                "dataset_version:",
                f"  metadata_path: '{metadata_file.as_posix()}'",
                "training:",
                "  test_size: 0.2",
                "  random_state: 42",
            ]
        ),
        encoding="utf-8",
    )
    return config_file
