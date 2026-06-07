"""Tests for V2 validation report persistence."""

import json
from pathlib import Path

from app.validation.reports import (
    ValidationIssue,
    build_report_paths,
    build_validation_report,
    build_validation_summary,
    save_validation_report,
    save_validation_summary,
)


def test_build_report_paths_from_config():
    config = {
        "validation": {
            "reports": {
                "dir": "reports",
                "json_file": "validation_report.json",
                "summary_file": "validation_summary.txt",
            }
        }
    }

    paths = build_report_paths(config)

    assert paths["json"] == Path("reports") / "validation_report.json"
    assert paths["summary"] == Path("reports") / "validation_summary.txt"


def test_save_validation_report_writes_json(tmp_path):
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
    )
    report_path = tmp_path / "validation_report.json"

    save_validation_report(report, report_path)

    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["status"] == "passed"
    assert data["rows"] == 20
    assert data["issues"] == []


def test_build_validation_summary_counts_issue_severities():
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

    summary = build_validation_summary(report)

    assert "status: failed" in summary
    assert "warning_count: 1" in summary
    assert "error_count: 1" in summary
    assert "duplicate_rows" in summary
    assert "duplicate_ids" in summary


def test_save_validation_summary_writes_text(tmp_path):
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
    )
    summary_path = tmp_path / "validation_summary.txt"

    save_validation_summary(report, summary_path)

    summary = summary_path.read_text(encoding="utf-8")
    assert "Validation Summary" in summary
    assert "status: passed" in summary
    assert "issues_total: 0" in summary
