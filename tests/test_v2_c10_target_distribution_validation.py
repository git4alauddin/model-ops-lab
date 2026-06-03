"""Tests for V2 target distribution validation."""

from pathlib import Path

import pandas as pd

from app.data import load_dataset
from app.validate_data import validate_dataset_readiness
from app.validation.checks import (
    load_validation_schema,
    validate_target_distribution,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_target_distribution_passes_for_sample_churn_dataset():
    dataframe = load_dataset(PROJECT_ROOT / "data" / "churn.csv")
    schema = load_validation_schema(
        PROJECT_ROOT / "schema_versions" / "customer_churn_v1.yaml"
    )

    issues = validate_target_distribution(dataframe, schema)

    assert issues == []


def test_validate_target_distribution_returns_error_for_single_class_target():
    dataframe = pd.DataFrame({"churn": [0, 0, 0, 0]})
    schema = _target_distribution_schema()

    issues = validate_target_distribution(dataframe, schema)

    assert len(issues) == 1
    assert issues[0].severity == "ERROR"
    assert issues[0].check == "target_distribution"
    assert "only one class" in issues[0].message


def test_validate_target_distribution_returns_warning_for_imbalanced_target():
    dataframe = pd.DataFrame({"churn": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]})
    schema = _target_distribution_schema()

    issues = validate_target_distribution(dataframe, schema)

    assert len(issues) == 1
    assert issues[0].severity == "WARNING"
    assert issues[0].check == "target_distribution"
    assert "minority_ratio=0.1000" in issues[0].message


def test_validate_target_distribution_skips_when_disabled():
    dataframe = pd.DataFrame({"churn": [0, 0, 0, 0]})
    schema = _target_distribution_schema(enabled=False)

    issues = validate_target_distribution(dataframe, schema)

    assert issues == []


def test_load_validation_schema_rejects_invalid_target_distribution_threshold(
    tmp_path,
):
    schema_file = tmp_path / "schema.yaml"
    schema_file.write_text(
        "\n".join(
            [
                "name: customer_churn",
                "version: v1",
                "target_column: churn",
                "columns:",
                "  churn:",
                "    dtype: integer",
                "    nullable: false",
                "quality_checks:",
                "  target_distribution:",
                "    enabled: true",
                "    min_class_ratio: 0.9",
                "    max_class_ratio: 0.8",
            ]
        ),
        encoding="utf-8",
    )

    try:
        load_validation_schema(schema_file)
    except ValueError as exc:
        assert "min_class_ratio must be less than max_class_ratio" in str(exc)
    else:
        raise AssertionError("Expected invalid target distribution thresholds to fail.")


def test_validate_dataset_readiness_warns_for_imbalanced_target(tmp_path):
    config_file, schema_file = _write_validation_inputs(
        tmp_path,
        [
            "customer_id,churn",
            "C001,0",
            "C002,0",
            "C003,0",
            "C004,0",
            "C005,0",
            "C006,0",
            "C007,0",
            "C008,0",
            "C009,0",
            "C010,1",
        ],
    )

    report = validate_dataset_readiness(config_file, schema_file)

    assert report.status == "passed"
    assert len(report.issues) == 1
    assert report.issues[0].severity == "WARNING"
    assert report.issues[0].check == "target_distribution"


def test_validate_dataset_readiness_fails_for_single_class_target(tmp_path):
    config_file, schema_file = _write_validation_inputs(
        tmp_path,
        [
            "customer_id,churn",
            "C001,0",
            "C002,0",
            "C003,0",
            "C004,0",
        ],
    )

    report = validate_dataset_readiness(config_file, schema_file)

    assert report.status == "failed"
    assert len(report.issues) == 1
    assert report.issues[0].severity == "ERROR"
    assert report.issues[0].check == "target_distribution"


def _target_distribution_schema(enabled: bool = True) -> dict:
    return {
        "target_column": "churn",
        "columns": {
            "churn": {
                "dtype": "integer",
                "nullable": False,
                "allowed_values": [0, 1],
            }
        },
        "quality_checks": {
            "target_distribution": {
                "enabled": enabled,
                "min_class_ratio": 0.2,
                "max_class_ratio": 0.8,
            }
        },
    }


def _write_validation_inputs(
    tmp_path: Path,
    dataset_lines: list[str],
) -> tuple[Path, Path]:
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    schema_dir = tmp_path / "schema_versions"
    config_dir.mkdir()
    data_dir.mkdir()
    schema_dir.mkdir()
    dataset_file = data_dir / "churn.csv"
    schema_file = schema_dir / "customer_churn_v1.yaml"
    config_file = config_dir / "training.yaml"

    dataset_file.write_text("\n".join(dataset_lines), encoding="utf-8")
    schema_file.write_text(
        "\n".join(
            [
                "name: customer_churn",
                "version: v1",
                "target_column: churn",
                "columns:",
                "  customer_id:",
                "    dtype: string",
                "    nullable: false",
                "  churn:",
                "    dtype: integer",
                "    nullable: false",
                "    allowed_values:",
                "      - 0",
                "      - 1",
                "quality_checks:",
                "  target_distribution:",
                "    enabled: true",
                "    min_class_ratio: 0.2",
                "    max_class_ratio: 0.8",
            ]
        ),
        encoding="utf-8",
    )
    config_file.write_text(
        "\n".join(
            [
                "dataset:",
                "  path: data/churn.csv",
                "  target_column: churn",
                "training:",
                "  test_size: 0.2",
                "  random_state: 42",
            ]
        ),
        encoding="utf-8",
    )

    return config_file, schema_file
