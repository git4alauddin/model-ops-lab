"""Tests for V2 structural schema validation."""

import pandas as pd

from app.validate_data import validate_dataset_readiness
from app.validation.checks import (
    validate_required_columns,
    validate_schema_columns,
    validate_unexpected_columns,
)


def test_validate_required_columns_detects_missing_column():
    dataframe = pd.DataFrame({"customer_id": ["C001"], "churn": [1]})
    schema = {
        "columns": {
            "customer_id": {"dtype": "string", "nullable": False},
            "tenure_months": {"dtype": "integer", "nullable": False},
            "churn": {"dtype": "integer", "nullable": False},
        }
    }

    issues = validate_required_columns(dataframe, schema)

    assert len(issues) == 1
    assert issues[0].severity == "ERROR"
    assert issues[0].check == "required_columns"
    assert "tenure_months" in issues[0].message


def test_validate_unexpected_columns_detects_extra_column():
    dataframe = pd.DataFrame(
        {
            "customer_id": ["C001"],
            "churn": [1],
            "leaked_churn_score": [0.99],
        }
    )
    schema = {
        "columns": {
            "customer_id": {"dtype": "string", "nullable": False},
            "churn": {"dtype": "integer", "nullable": False},
        }
    }

    issues = validate_unexpected_columns(dataframe, schema)

    assert len(issues) == 1
    assert issues[0].severity == "ERROR"
    assert issues[0].check == "unexpected_columns"
    assert "leaked_churn_score" in issues[0].message


def test_validate_schema_columns_passes_for_matching_structure():
    dataframe = pd.DataFrame({"customer_id": ["C001"], "churn": [1]})
    schema = {
        "columns": {
            "customer_id": {"dtype": "string", "nullable": False},
            "churn": {"dtype": "integer", "nullable": False},
        }
    }

    issues = validate_schema_columns(dataframe, schema)

    assert issues == []


def test_validate_dataset_readiness_failed_report_for_bad_structure(tmp_path):
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
                "customer_id,churn,unexpected_feature",
                "C001,1,abc",
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
    assert len(report.issues) == 2
    assert {issue.check for issue in report.issues} == {
        "required_columns",
        "unexpected_columns",
    }
