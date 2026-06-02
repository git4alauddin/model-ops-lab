"""Tests for V2 numeric range validation."""

from pathlib import Path

import pandas as pd

from app.data import load_dataset
from app.validate_data import validate_dataset_readiness
from app.validation.checks import load_validation_schema, validate_numeric_ranges

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_validate_numeric_ranges_passes_for_sample_churn_dataset():
    dataframe = load_dataset(PROJECT_ROOT / "data" / "churn.csv")
    schema = load_validation_schema(
        PROJECT_ROOT / "schema_versions" / "customer_churn_v1.yaml"
    )

    issues = validate_numeric_ranges(dataframe, schema)

    assert issues == []


def test_validate_numeric_ranges_detects_below_minimum():
    dataframe = pd.DataFrame({"tenure_months": [-1], "churn": [1]})
    schema = {
        "columns": {
            "tenure_months": {
                "dtype": "integer",
                "nullable": False,
                "min": 0,
                "max": 120,
            },
            "churn": {"dtype": "integer", "nullable": False},
        }
    }

    issues = validate_numeric_ranges(dataframe, schema)

    assert len(issues) == 1
    assert issues[0].severity == "ERROR"
    assert issues[0].check == "numeric_ranges"
    assert "below min 0" in issues[0].message


def test_validate_numeric_ranges_detects_above_maximum():
    dataframe = pd.DataFrame({"tenure_months": [121], "churn": [1]})
    schema = {
        "columns": {
            "tenure_months": {
                "dtype": "integer",
                "nullable": False,
                "min": 0,
                "max": 120,
            },
            "churn": {"dtype": "integer", "nullable": False},
        }
    }

    issues = validate_numeric_ranges(dataframe, schema)

    assert len(issues) == 1
    assert "above max 120" in issues[0].message


def test_validate_numeric_ranges_detects_negative_charge():
    dataframe = pd.DataFrame({"monthly_charges": [-10.5], "churn": [1]})
    schema = {
        "columns": {
            "monthly_charges": {
                "dtype": "float",
                "nullable": False,
                "min": 0,
            },
            "churn": {"dtype": "integer", "nullable": False},
        }
    }

    issues = validate_numeric_ranges(dataframe, schema)

    assert len(issues) == 1
    assert "monthly_charges" in issues[0].message
    assert "below min 0" in issues[0].message


def test_validate_dataset_readiness_failed_report_for_range_violation(tmp_path):
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    schema_dir = tmp_path / "schema_versions"
    config_dir.mkdir()
    data_dir.mkdir()
    schema_dir.mkdir()
    dataset_file = data_dir / "churn.csv"
    schema_file = schema_dir / "customer_churn_v1.yaml"
    config_file = config_dir / "training.yaml"

    dataset_file.write_text(
        "\n".join(
            [
                "customer_id,tenure_months,churn",
                "C001,121,1",
            ]
        ),
        encoding="utf-8",
    )
    schema_file.write_text(
        "\n".join(
            [
                "name: customer_churn",
                "version: v1",
                "columns:",
                "  customer_id:",
                "    dtype: string",
                "    nullable: false",
                "  tenure_months:",
                "    dtype: integer",
                "    nullable: false",
                "    min: 0",
                "    max: 120",
                "  churn:",
                "    dtype: integer",
                "    nullable: false",
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

    report = validate_dataset_readiness(config_file, schema_file)

    assert report.status == "failed"
    assert len(report.issues) == 1
    assert report.issues[0].check == "numeric_ranges"
    assert "tenure_months" in report.issues[0].message
