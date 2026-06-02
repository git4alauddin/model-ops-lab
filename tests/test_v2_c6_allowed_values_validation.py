"""Tests for V2 allowed-value validation."""

from pathlib import Path

import pandas as pd

from app.data import load_dataset
from app.validate_data import validate_dataset_readiness
from app.validation.checks import load_validation_schema, validate_allowed_values

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_validate_allowed_values_passes_for_sample_churn_dataset():
    dataframe = load_dataset(PROJECT_ROOT / "data" / "churn.csv")
    schema = load_validation_schema(
        PROJECT_ROOT / "schema_versions" / "customer_churn_v1.yaml"
    )

    issues = validate_allowed_values(dataframe, schema)

    assert issues == []


def test_validate_allowed_values_detects_invalid_contract_type():
    dataframe = pd.DataFrame({"contract_type": ["weekly"]})
    schema = {
        "columns": {
            "contract_type": {
                "dtype": "category",
                "nullable": False,
                "allowed_values": ["month_to_month", "one_year", "two_year"],
            }
        }
    }

    issues = validate_allowed_values(dataframe, schema)

    assert len(issues) == 1
    assert issues[0].severity == "ERROR"
    assert issues[0].check == "allowed_values"
    assert "contract_type" in issues[0].message
    assert "weekly" in issues[0].message


def test_validate_allowed_values_detects_invalid_internet_service():
    dataframe = pd.DataFrame({"internet_service": ["satellite"]})
    schema = {
        "columns": {
            "internet_service": {
                "dtype": "category",
                "nullable": False,
                "allowed_values": ["dsl", "fiber_optic"],
            }
        }
    }

    issues = validate_allowed_values(dataframe, schema)

    assert len(issues) == 1
    assert "satellite" in issues[0].message


def test_validate_allowed_values_detects_invalid_target_value():
    dataframe = pd.DataFrame({"churn": [2]})
    schema = {
        "columns": {
            "churn": {
                "dtype": "integer",
                "nullable": False,
                "allowed_values": [0, 1],
            }
        }
    }

    issues = validate_allowed_values(dataframe, schema)

    assert len(issues) == 1
    assert "churn" in issues[0].message
    assert "2" in issues[0].message


def test_validate_allowed_values_detects_invalid_boolean_value():
    dataframe = pd.DataFrame({"is_senior": [True, False, "yes"]})
    schema = {
        "columns": {
            "is_senior": {
                "dtype": "boolean",
                "nullable": False,
                "allowed_values": [True, False],
            }
        }
    }

    issues = validate_allowed_values(dataframe, schema)

    assert len(issues) == 1
    assert "yes" in issues[0].message


def test_validate_dataset_readiness_failed_report_for_invalid_allowed_value(tmp_path):
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
                "customer_id,contract_type,churn",
                "C001,weekly,1",
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
                "  contract_type:",
                "    dtype: category",
                "    nullable: false",
                "    allowed_values:",
                "      - month_to_month",
                "      - one_year",
                "      - two_year",
                "  churn:",
                "    dtype: integer",
                "    nullable: false",
                "    allowed_values:",
                "      - 0",
                "      - 1",
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
    assert report.issues[0].check == "allowed_values"
    assert "contract_type" in report.issues[0].message
