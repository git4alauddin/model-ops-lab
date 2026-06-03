"""Tests for V2 null percentage validation."""

from pathlib import Path

import pandas as pd

from app.data import load_dataset
from app.validate_data import validate_dataset_readiness
from app.validation.checks import (
    load_validation_schema,
    validate_null_percentages,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_null_percentage_validation_passes_for_sample_churn_dataset():
    dataframe = load_dataset(PROJECT_ROOT / "data" / "churn.csv")
    schema = load_validation_schema(
        PROJECT_ROOT / "schema_versions" / "customer_churn_v1.yaml"
    )

    issues = validate_null_percentages(dataframe, schema)

    assert issues == []


def test_validate_null_percentages_returns_warning_for_moderate_missingness():
    dataframe = pd.DataFrame({"support_tier": ["basic", "plus", None, "basic"]})
    schema = _null_percentage_schema()

    issues = validate_null_percentages(dataframe, schema)

    assert len(issues) == 1
    assert issues[0].severity == "WARNING"
    assert issues[0].check == "null_percentages"
    assert "support_tier" in issues[0].message
    assert "0.2500" in issues[0].message


def test_validate_null_percentages_returns_error_for_high_missingness():
    dataframe = pd.DataFrame({"support_tier": ["basic", None, None, None]})
    schema = _null_percentage_schema()

    issues = validate_null_percentages(dataframe, schema)

    assert len(issues) == 1
    assert issues[0].severity == "ERROR"
    assert issues[0].check == "null_percentages"
    assert "0.7500" in issues[0].message


def test_validate_null_percentages_skips_non_nullable_columns_without_override():
    dataframe = pd.DataFrame({"customer_id": ["C001", None, "C003"]})
    schema = {
        "columns": {
            "customer_id": {
                "dtype": "string",
                "nullable": False,
            }
        },
        "quality_checks": {
            "null_percentages": {
                "enabled": True,
                "default_warning_ratio": 0.1,
                "default_error_ratio": 0.3,
            }
        },
    }

    issues = validate_null_percentages(dataframe, schema)

    assert issues == []


def test_validate_null_percentages_skips_when_disabled():
    dataframe = pd.DataFrame({"support_tier": [None, None, None]})
    schema = _null_percentage_schema(enabled=False)

    issues = validate_null_percentages(dataframe, schema)

    assert issues == []


def test_load_validation_schema_rejects_invalid_null_percentage_threshold(
    tmp_path,
):
    schema_file = tmp_path / "schema.yaml"
    schema_file.write_text(
        "\n".join(
            [
                "name: customer_churn",
                "version: v1",
                "columns:",
                "  support_tier:",
                "    dtype: category",
                "    nullable: true",
                "quality_checks:",
                "  null_percentages:",
                "    enabled: true",
                "    default_warning_ratio: 0.4",
                "    default_error_ratio: 0.3",
            ]
        ),
        encoding="utf-8",
    )

    try:
        load_validation_schema(schema_file)
    except ValueError as exc:
        assert "default_warning_ratio must be less than default_error_ratio" in str(
            exc
        )
    else:
        raise AssertionError("Expected invalid null percentage thresholds to fail.")


def test_validate_dataset_readiness_warns_for_moderate_null_percentage(tmp_path):
    config_file, schema_file = _write_validation_inputs(
        tmp_path,
        [
            "customer_id,support_tier",
            "C001,basic",
            "C002,plus",
            "C003,",
            "C004,basic",
        ],
    )

    report = validate_dataset_readiness(config_file, schema_file)

    assert report.status == "passed"
    assert len(report.issues) == 1
    assert report.issues[0].severity == "WARNING"
    assert report.issues[0].check == "null_percentages"


def test_validate_dataset_readiness_fails_for_high_null_percentage(tmp_path):
    config_file, schema_file = _write_validation_inputs(
        tmp_path,
        [
            "customer_id,support_tier",
            "C001,basic",
            "C002,",
            "C003,",
            "C004,",
        ],
    )

    report = validate_dataset_readiness(config_file, schema_file)

    assert report.status == "failed"
    assert len(report.issues) == 1
    assert report.issues[0].severity == "ERROR"
    assert report.issues[0].check == "null_percentages"


def _null_percentage_schema(enabled: bool = True) -> dict:
    return {
        "columns": {
            "support_tier": {
                "dtype": "category",
                "nullable": True,
            }
        },
        "quality_checks": {
            "null_percentages": {
                "enabled": enabled,
                "default_warning_ratio": 0.2,
                "default_error_ratio": 0.5,
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
                "columns:",
                "  customer_id:",
                "    dtype: string",
                "    nullable: false",
                "  support_tier:",
                "    dtype: category",
                "    nullable: true",
                "quality_checks:",
                "  null_percentages:",
                "    enabled: true",
                "    default_warning_ratio: 0.2",
                "    default_error_ratio: 0.5",
            ]
        ),
        encoding="utf-8",
    )
    config_file.write_text(
        "\n".join(
            [
                "dataset:",
                "  path: data/churn.csv",
                "  target_column: support_tier",
                "training:",
                "  test_size: 0.2",
                "  random_state: 42",
            ]
        ),
        encoding="utf-8",
    )

    return config_file, schema_file
