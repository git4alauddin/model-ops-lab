"""Validation report structures."""

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any


class ValidationReportError(ValueError):
    """Raised when validation report persistence fails."""


@dataclass(frozen=True)
class ValidationIssue:
    """Single validation finding."""

    severity: str
    check: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    """Serializable validation report summary."""

    status: str
    dataset_path: str
    schema_path: str
    schema_version: str
    rows: int
    columns: int
    issues: list[ValidationIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready report dictionary."""
        return asdict(self)


def build_validation_report(
    dataset_path: str,
    schema_path: str,
    schema_version: str,
    rows: int,
    columns: int,
    issues: list[ValidationIssue] | None = None,
) -> ValidationReport:
    """Build a validation report with status derived from issue severity."""
    report_issues = issues or []
    blocking_severities = {"ERROR", "CRITICAL"}
    status = (
        "failed"
        if any(issue.severity in blocking_severities for issue in report_issues)
        else "passed"
    )

    return ValidationReport(
        status=status,
        dataset_path=dataset_path,
        schema_path=schema_path,
        schema_version=schema_version,
        rows=rows,
        columns=columns,
        issues=report_issues,
    )


def build_report_paths(config: dict[str, Any]) -> dict[str, Path]:
    """Build validation report file paths from config."""
    validation_config = config.get("validation")
    if not isinstance(validation_config, dict):
        raise ValidationReportError("Missing validation config section.")

    reports_config = validation_config.get("reports")
    if not isinstance(reports_config, dict):
        raise ValidationReportError("Missing validation.reports config section.")

    required_keys = ("dir", "json_file", "summary_file")
    missing_keys = [key for key in required_keys if not reports_config.get(key)]
    if missing_keys:
        raise ValidationReportError(
            f"Missing validation report config keys: {missing_keys}"
        )

    report_dir = Path(reports_config["dir"])
    return {
        "json": report_dir / reports_config["json_file"],
        "summary": report_dir / reports_config["summary_file"],
    }


def save_validation_report(report: ValidationReport, path: str | Path) -> None:
    """Persist the validation report as JSON."""
    report_path = Path(path)
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8") as file:
            json.dump(report.to_dict(), file, indent=2)
    except (OSError, TypeError) as exc:
        raise ValidationReportError(
            f"Failed to save validation report: {report_path}"
        ) from exc


def build_validation_summary(report: ValidationReport) -> str:
    """Build a human-readable validation summary."""
    severity_counts = _count_issue_severities(report.issues)
    lines = [
        "Validation Summary",
        f"status: {report.status}",
        f"dataset_path: {report.dataset_path}",
        f"schema_path: {report.schema_path}",
        f"schema_version: {report.schema_version}",
        f"rows: {report.rows}",
        f"columns: {report.columns}",
        f"issues_total: {len(report.issues)}",
        f"info_count: {severity_counts['INFO']}",
        f"warning_count: {severity_counts['WARNING']}",
        f"error_count: {severity_counts['ERROR']}",
        f"critical_count: {severity_counts['CRITICAL']}",
    ]

    if report.issues:
        lines.append("issues:")
        for issue in report.issues:
            lines.append(f"- {issue.severity} | {issue.check} | {issue.message}")

    return "\n".join(lines)


def save_validation_summary(report: ValidationReport, path: str | Path) -> None:
    """Persist the validation report as a text summary."""
    summary_path = Path(path)
    try:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            build_validation_summary(report),
            encoding="utf-8",
        )
    except OSError as exc:
        raise ValidationReportError(
            f"Failed to save validation summary: {summary_path}"
        ) from exc


def _count_issue_severities(issues: list[ValidationIssue]) -> dict[str, int]:
    counts = {"INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}
    for issue in issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1
    return counts
