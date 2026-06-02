"""Validation report structures."""

from dataclasses import asdict, dataclass, field
from typing import Any


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
