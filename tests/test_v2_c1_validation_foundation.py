"""Tests for V2 validation foundation."""

from pathlib import Path

from app.validate_data import validate_dataset_readiness
from app.validation.checks import ValidationError, load_validation_schema
from app.validation.reports import ValidationIssue, build_validation_report

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_load_validation_schema_success():
    schema = load_validation_schema(
        PROJECT_ROOT / "schema_versions" / "customer_churn_v1.yaml"
    )

    assert schema["name"] == "customer_churn"
    assert schema["version"] == "v1"
    assert "churn" in schema["columns"]


def test_load_validation_schema_requires_column_dtype(tmp_path):
    schema_file = tmp_path / "schema.yaml"
    schema_file.write_text(
        "\n".join(
            [
                "name: customer_churn",
                "version: v1",
                "columns:",
                "  churn:",
                "    nullable: false",
            ]
        ),
        encoding="utf-8",
    )

    try:
        load_validation_schema(schema_file)
    except ValidationError as exc:
        assert "Missing dtype" in str(exc)
    else:
        raise AssertionError("Expected ValidationError for missing dtype.")


def test_build_validation_report_status_from_issues():
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        issues=[
            ValidationIssue(
                severity="ERROR",
                check="required_columns",
                message="missing required column: churn",
            )
        ],
    )

    assert report.status == "failed"
    assert report.to_dict()["issues"][0]["severity"] == "ERROR"


def test_validate_dataset_readiness_success():
    report = validate_dataset_readiness(
        PROJECT_ROOT / "configs" / "training.yaml",
        PROJECT_ROOT / "schema_versions" / "customer_churn_v1.yaml",
    )

    assert report.status == "passed"
    assert report.schema_version == "v1"
    assert report.rows == 20
    assert report.columns == 9
