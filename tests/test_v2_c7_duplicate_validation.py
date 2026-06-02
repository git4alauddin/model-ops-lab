"""Tests for V2 duplicate validation."""

from pathlib import Path

import pandas as pd

from app.data import load_dataset
from app.validate_data import validate_dataset_readiness
from app.validation.checks import (
    load_validation_schema,
    validate_duplicate_ids,
    validate_duplicate_rows,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_duplicate_validation_passes_for_sample_churn_dataset():
    dataframe = load_dataset(PROJECT_ROOT / "data" / "churn.csv")
    schema = load_validation_schema(
        PROJECT_ROOT / "schema_versions" / "customer_churn_v1.yaml"
    )

    assert validate_duplicate_rows(dataframe) == []
    assert validate_duplicate_ids(dataframe, schema) == []


def test_validate_duplicate_rows_returns_warning():
    dataframe = pd.DataFrame(
        [
            {"customer_id": "C001", "churn": 1},
            {"customer_id": "C001", "churn": 1},
        ]
    )

    issues = validate_duplicate_rows(dataframe)

    assert len(issues) == 1
    assert issues[0].severity == "WARNING"
    assert issues[0].check == "duplicate_rows"
    assert "1 duplicate row" in issues[0].message


def test_validate_duplicate_ids_returns_error():
    dataframe = pd.DataFrame(
        {
            "customer_id": ["C001", "C001"],
            "churn": [1, 0],
        }
    )
    schema = {"id_column": "customer_id", "columns": {}}

    issues = validate_duplicate_ids(dataframe, schema)

    assert len(issues) == 1
    assert issues[0].severity == "ERROR"
    assert issues[0].check == "duplicate_ids"
    assert "customer_id" in issues[0].message


def test_validate_dataset_readiness_warning_report_for_duplicate_rows(tmp_path):
    config_file, schema_file = _write_validation_inputs(
        tmp_path,
        [
            "customer_id,churn",
            "C001,1",
            "C001,1",
        ],
        include_id_column=False,
    )

    report = validate_dataset_readiness(config_file, schema_file)

    assert report.status == "passed"
    assert len(report.issues) == 1
    assert report.issues[0].severity == "WARNING"
    assert report.issues[0].check == "duplicate_rows"


def test_validate_dataset_readiness_failed_report_for_duplicate_ids(tmp_path):
    config_file, schema_file = _write_validation_inputs(
        tmp_path,
        [
            "customer_id,churn",
            "C001,1",
            "C001,0",
        ],
    )

    report = validate_dataset_readiness(config_file, schema_file)

    assert report.status == "failed"
    assert len(report.issues) == 1
    assert report.issues[0].severity == "ERROR"
    assert report.issues[0].check == "duplicate_ids"


def _write_validation_inputs(
    tmp_path: Path,
    dataset_lines: list[str],
    include_id_column: bool = True,
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
    schema_lines = [
        "name: customer_churn",
        "version: v1",
    ]
    if include_id_column:
        schema_lines.append("id_column: customer_id")
    schema_lines.extend(
        [
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
        ]
    )
    schema_file.write_text(
        "\n".join(schema_lines),
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
