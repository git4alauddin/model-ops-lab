"""Tests for V2 training validation gate."""

from pathlib import Path

from app.train import (
    ValidationGateError,
    count_validation_issues,
    enforce_validation_gate,
    resolve_validation_schema_path,
)
from app.validate_data import DEFAULT_SCHEMA_PATH
from app.validation.reports import ValidationIssue, build_validation_report


def test_validation_gate_allows_clean_report():
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
    )

    enforce_validation_gate(report)


def test_validation_gate_allows_warning_only_report():
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        issues=[
            ValidationIssue(
                severity="WARNING",
                check="duplicate_rows",
                message="dataset contains 1 duplicate row",
            )
        ],
    )

    enforce_validation_gate(report)


def test_validation_gate_blocks_failed_report():
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        issues=[
            ValidationIssue(
                severity="ERROR",
                check="duplicate_ids",
                message="duplicate customer_id",
            )
        ],
    )

    try:
        enforce_validation_gate(report)
    except ValidationGateError as exc:
        assert "validation status is failed" in str(exc)
    else:
        raise AssertionError("Expected ValidationGateError for failed validation.")


def test_count_validation_issues_by_severity():
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        issues=[
            ValidationIssue(
                severity="WARNING",
                check="duplicate_rows",
                message="dataset contains 1 duplicate row",
            ),
            ValidationIssue(
                severity="ERROR",
                check="duplicate_ids",
                message="duplicate customer_id",
            ),
        ],
    )

    counts = count_validation_issues(report)

    assert counts["WARNING"] == 1
    assert counts["ERROR"] == 1
    assert counts["INFO"] == 0
    assert counts["CRITICAL"] == 0


def test_resolve_validation_schema_path_from_config():
    schema_path = resolve_validation_schema_path(
        {"validation": {"schema_path": "schema_versions/customer_churn_v1.yaml"}}
    )

    assert schema_path == Path("schema_versions/customer_churn_v1.yaml")


def test_resolve_validation_schema_path_default():
    schema_path = resolve_validation_schema_path({})

    assert schema_path == DEFAULT_SCHEMA_PATH
