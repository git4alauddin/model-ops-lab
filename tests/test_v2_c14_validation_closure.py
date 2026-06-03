"""Closure tests for V2 validation checklist coverage."""

from pathlib import Path

from app.data import DataError
from app.train import ValidationGateError, enforce_validation_gate
from app.validate_data import validate_dataset_readiness
from app.validation.reports import ValidationIssue, build_validation_report

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_info_severity_is_counted_without_blocking_report():
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        issues=[
            ValidationIssue(
                severity="INFO",
                check="schema_version",
                message="schema version recorded",
            )
        ],
    )

    assert report.status == "passed"
    assert report.issue_counts["INFO"] == 1


def test_critical_severity_fails_report_and_blocks_training_gate():
    report = build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        issues=[
            ValidationIssue(
                severity="CRITICAL",
                check="dataset_readability",
                message="dataset cannot be safely loaded",
            )
        ],
    )

    assert report.status == "failed"
    assert report.issue_counts["CRITICAL"] == 1

    try:
        enforce_validation_gate(report)
    except ValidationGateError as exc:
        assert "validation status is failed" in str(exc)
    else:
        raise AssertionError("Expected ValidationGateError for CRITICAL validation.")


def test_corrupted_dataset_is_rejected_safely(tmp_path):
    corrupted_dataset = tmp_path / "corrupted.csv"
    corrupted_dataset.write_bytes(b"\x80\x80")
    config_file = tmp_path / "training.yaml"
    config_file.write_text(
        "\n".join(
            [
                "dataset:",
                f"  path: '{corrupted_dataset.as_posix()}'",
                "  target_column: churn",
                "training:",
                "  test_size: 0.2",
                "  random_state: 42",
            ]
        ),
        encoding="utf-8",
    )

    try:
        validate_dataset_readiness(
            config_file,
            PROJECT_ROOT / "schema_versions" / "customer_churn_v1.yaml",
        )
    except DataError as exc:
        assert "Dataset could not be parsed" in str(exc)
    else:
        raise AssertionError("Expected DataError for corrupted dataset.")
