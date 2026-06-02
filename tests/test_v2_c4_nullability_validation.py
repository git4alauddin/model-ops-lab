"""Tests for V2 nullability validation."""

from pathlib import Path

import pandas as pd

from app.data import load_dataset
from app.validate_data import validate_dataset_readiness
from app.validation.checks import load_validation_schema, validate_nullable_columns

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_validate_nullable_columns_passes_for_sample_churn_dataset():
    dataframe = load_dataset(PROJECT_ROOT / "data" / "churn.csv")
    schema = load_validation_schema(
        PROJECT_ROOT / "schema_versions" / "customer_churn_v1.yaml"
    )

    issues = validate_nullable_columns(dataframe, schema)

    assert issues == []


def test_validate_nullable_columns_detects_null_in_required_column():
    dataframe = pd.DataFrame({"customer_id": ["C001"], "churn": [None]})
    schema = {
        "columns": {
            "customer_id": {"dtype": "string", "nullable": False},
            "churn": {"dtype": "integer", "nullable": False},
        }
    }

    issues = validate_nullable_columns(dataframe, schema)

    assert len(issues) == 1
    assert issues[0].severity == "ERROR"
    assert issues[0].check == "nullable_columns"
    assert "churn" in issues[0].message
    assert "1 null" in issues[0].message


def test_validate_nullable_columns_allows_null_when_schema_allows_it():
    dataframe = pd.DataFrame({"customer_id": ["C001"], "notes": [None]})
    schema = {
        "columns": {
            "customer_id": {"dtype": "string", "nullable": False},
            "notes": {"dtype": "string", "nullable": True},
        }
    }

    issues = validate_nullable_columns(dataframe, schema)

    assert issues == []


def test_validate_dataset_readiness_failed_report_for_null_violation(tmp_path):
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
                "C001,,1",
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
                "    dtype: float",
                "    nullable: false",
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
    assert report.issues[0].check == "nullable_columns"
    assert "tenure_months" in report.issues[0].message
