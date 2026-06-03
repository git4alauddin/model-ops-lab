"""Tests for V2 validation report metadata."""

import json

from app.validation.reports import (
    ValidationIssue,
    build_validation_report,
    build_validation_summary,
    save_validation_report,
)


def test_validation_report_includes_runtime_metadata():
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        generated_at="2026-06-03T00:00:00+00:00",
        duration_seconds=0.123456,
    )

    assert report.generated_at == "2026-06-03T00:00:00+00:00"
    assert report.duration_seconds == 0.123456
    assert report.issue_counts == {
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0,
    }


def test_validation_report_counts_issue_severities():
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

    assert report.status == "failed"
    assert report.issue_counts["WARNING"] == 1
    assert report.issue_counts["ERROR"] == 1


def test_save_validation_report_persists_metadata(tmp_path):
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        generated_at="2026-06-03T00:00:00+00:00",
        duration_seconds=0.5,
    )
    report_path = tmp_path / "validation_report.json"

    save_validation_report(report, report_path)

    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["generated_at"] == "2026-06-03T00:00:00+00:00"
    assert data["duration_seconds"] == 0.5
    assert data["issue_counts"]["WARNING"] == 0


def test_validation_summary_includes_metadata():
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        generated_at="2026-06-03T00:00:00+00:00",
        duration_seconds=0.25,
    )

    summary = build_validation_summary(report)

    assert "generated_at: 2026-06-03T00:00:00+00:00" in summary
    assert "duration_seconds: 0.250000" in summary
