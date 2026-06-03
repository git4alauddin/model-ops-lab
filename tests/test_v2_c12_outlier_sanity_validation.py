"""Tests for V2 outlier sanity validation."""

from pathlib import Path

import pandas as pd

from app.data import load_dataset
from app.validate_data import validate_dataset_readiness
from app.validation.checks import (
    load_validation_schema,
    validate_outlier_sanity,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_outlier_sanity_passes_for_sample_churn_dataset():
    dataframe = load_dataset(PROJECT_ROOT / "data" / "churn.csv")
    schema = load_validation_schema(
        PROJECT_ROOT / "schema_versions" / "customer_churn_v1.yaml"
    )

    issues = validate_outlier_sanity(dataframe, schema)

    assert issues == []


def test_validate_outlier_sanity_returns_warning_for_high_numeric_value():
    dataframe = pd.DataFrame({"monthly_charges": [40.0, 55.0, 5000.0]})
    schema = _outlier_sanity_schema()

    issues = validate_outlier_sanity(dataframe, schema)

    assert len(issues) == 1
    assert issues[0].severity == "WARNING"
    assert issues[0].check == "outlier_sanity"
    assert "monthly_charges" in issues[0].message
    assert "above" in issues[0].message


def test_validate_outlier_sanity_returns_warning_for_low_numeric_value():
    dataframe = pd.DataFrame({"monthly_charges": [-10.0, 40.0, 55.0]})
    schema = _outlier_sanity_schema(warning_min=0, warning_max=300)

    issues = validate_outlier_sanity(dataframe, schema)

    assert len(issues) == 1
    assert issues[0].severity == "WARNING"
    assert "below" in issues[0].message


def test_validate_outlier_sanity_skips_when_disabled():
    dataframe = pd.DataFrame({"monthly_charges": [5000.0]})
    schema = _outlier_sanity_schema(enabled=False)

    issues = validate_outlier_sanity(dataframe, schema)

    assert issues == []


def test_load_validation_schema_rejects_invalid_outlier_threshold(
    tmp_path,
):
    schema_file = tmp_path / "schema.yaml"
    schema_file.write_text(
        "\n".join(
            [
                "name: customer_churn",
                "version: v1",
                "columns:",
                "  monthly_charges:",
                "    dtype: float",
                "    nullable: false",
                "quality_checks:",
                "  outlier_sanity:",
                "    enabled: true",
                "    columns:",
                "      monthly_charges:",
                "        warning_min: 300",
                "        warning_max: 100",
            ]
        ),
        encoding="utf-8",
    )

    try:
        load_validation_schema(schema_file)
    except ValueError as exc:
        assert "warning_min" in str(exc)
        assert "must be less than warning_max" in str(exc)
    else:
        raise AssertionError("Expected invalid outlier thresholds to fail.")


def test_validate_dataset_readiness_warns_for_outlier_value(tmp_path):
    config_file, schema_file = _write_validation_inputs(
        tmp_path,
        [
            "customer_id,monthly_charges",
            "C001,45.0",
            "C002,50.0",
            "C003,5000.0",
        ],
    )

    report = validate_dataset_readiness(config_file, schema_file)

    assert report.status == "passed"
    assert len(report.issues) == 1
    assert report.issues[0].severity == "WARNING"
    assert report.issues[0].check == "outlier_sanity"


def _outlier_sanity_schema(
    enabled: bool = True,
    warning_min: float | None = None,
    warning_max: float | None = 300,
) -> dict:
    thresholds = {}
    if warning_min is not None:
        thresholds["warning_min"] = warning_min
    if warning_max is not None:
        thresholds["warning_max"] = warning_max

    return {
        "columns": {
            "monthly_charges": {
                "dtype": "float",
                "nullable": False,
                "min": 0,
            }
        },
        "quality_checks": {
            "outlier_sanity": {
                "enabled": enabled,
                "columns": {
                    "monthly_charges": thresholds,
                },
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
                "  monthly_charges:",
                "    dtype: float",
                "    nullable: false",
                "    min: 0",
                "quality_checks:",
                "  outlier_sanity:",
                "    enabled: true",
                "    columns:",
                "      monthly_charges:",
                "        warning_max: 300",
            ]
        ),
        encoding="utf-8",
    )
    config_file.write_text(
        "\n".join(
            [
                "dataset:",
                "  path: data/churn.csv",
                "  target_column: monthly_charges",
                "training:",
                "  test_size: 0.2",
                "  random_state: 42",
            ]
        ),
        encoding="utf-8",
    )

    return config_file, schema_file
