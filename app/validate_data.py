"""V2 validation entrypoint for dataset readiness checks."""

from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any, cast

from app.config import ConfigError, load_config
from app.data import DataError, load_dataset
from app.dataset_registry import (
    build_dataset_version_snapshot,
    DatasetRegistryError,
    load_dataset_version_metadata,
    resolve_dataset_version_metadata_path,
)
from app.utils.logger import build_log_path, get_logger
from app.validation.checks import (
    ValidationError,
    load_validation_schema,
    validate_allowed_values,
    validate_column_dtypes,
    validate_duplicate_ids,
    validate_duplicate_rows,
    validate_nullable_columns,
    validate_null_percentages,
    validate_numeric_ranges,
    validate_outlier_sanity,
    validate_schema_columns,
    validate_target_distribution,
)
from app.validation.reports import (
    ValidationReport,
    ValidationReportError,
    build_report_paths,
    build_validation_report,
    save_validation_report,
    save_validation_summary,
)

LOGGER_NAME = "modelopslab.validation"
DEFAULT_CONFIG_PATH = Path("configs/training.yaml")
DEFAULT_SCHEMA_PATH = Path("schema_versions/customer_churn_v1.yaml")


def validate_dataset_readiness(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
) -> ValidationReport:
    """Load validation inputs and return the initial dataset readiness report."""
    validation_started_at = datetime.now(UTC).isoformat()
    started_at = perf_counter()
    resolved_config_path = Path(config_path)
    resolved_schema_path = Path(schema_path)
    config = load_config(resolved_config_path)
    schema = load_validation_schema(resolved_schema_path)
    dataset_version_metadata_path = resolve_dataset_version_metadata_path(config)
    dataset_version_metadata = load_dataset_version_metadata(
        dataset_version_metadata_path
    )
    dataset_version_snapshot = build_dataset_version_snapshot(
        dataset_version_metadata_path,
        dataset_version_metadata,
    )
    dataset_config = cast(dict[str, Any], config["dataset"])
    dataset_path = _resolve_project_path(
        resolved_config_path,
        cast(str, dataset_config["path"]),
    )
    dataframe = load_dataset(dataset_path)
    issues = validate_schema_columns(dataframe, schema)
    issues.extend(validate_column_dtypes(dataframe, schema))
    issues.extend(validate_nullable_columns(dataframe, schema))
    issues.extend(validate_null_percentages(dataframe, schema))
    issues.extend(validate_numeric_ranges(dataframe, schema))
    issues.extend(validate_outlier_sanity(dataframe, schema))
    issues.extend(validate_allowed_values(dataframe, schema))
    issues.extend(validate_duplicate_rows(dataframe))
    issues.extend(validate_duplicate_ids(dataframe, schema))
    issues.extend(validate_target_distribution(dataframe, schema))

    return build_validation_report(
        dataset_path=str(dataset_path),
        schema_path=str(resolved_schema_path),
        schema_version=cast(str, schema["version"]),
        rows=len(dataframe),
        columns=len(dataframe.columns),
        issues=issues,
        generated_at=validation_started_at,
        duration_seconds=perf_counter() - started_at,
        dataset_version=dataset_version_snapshot,
    )


def _resolve_project_path(config_path: Path, configured_path: str) -> Path:
    path = Path(configured_path)
    if path.is_absolute():
        return path

    project_root = config_path.parent.parent
    return project_root / path


def _count_validation_issues(report: ValidationReport) -> dict[str, int]:
    return report.issue_counts


def _format_log_section(title: str, values: dict[str, Any]) -> str:
    """Format a readable key-value section for runtime logs."""
    key_width = max(len(key) for key in values)
    lines = [f"[{title}]"]
    lines.extend(f"{key:<{key_width}} : {value}" for key, value in values.items())
    return "\n".join(lines)


def _format_issue_summary(report: ValidationReport) -> str:
    lines = ["[ISSUES]"]
    for issue in report.issues:
        lines.append(f"- {issue.severity} | {issue.check} | {issue.message}")
    return "\n".join(lines)


def main() -> None:
    """Run the V2 validation scaffold from the command line."""
    logger = get_logger(LOGGER_NAME)

    try:
        config = load_config(DEFAULT_CONFIG_PATH)
        log_path = build_log_path(config)
        logger = get_logger(LOGGER_NAME, log_path)
        run_started_at = datetime.now(UTC).isoformat()
        logger.info(
            "===== RUN STARTED %s | workflow=validation =====",
            run_started_at,
        )
        report = validate_dataset_readiness(DEFAULT_CONFIG_PATH, DEFAULT_SCHEMA_PATH)
        report_paths = build_report_paths(config)
        save_validation_report(report, report_paths["json"])
        save_validation_summary(report, report_paths["summary"])
        issue_counts = _count_validation_issues(report)
        logger.info(_format_log_section("RUNTIME", {"log_file": log_path}))
        logger.info(
            _format_log_section(
                "VALIDATION",
                {
                    "status": report.status,
                    "issues": len(report.issues),
                    "info": issue_counts["INFO"],
                    "warnings": issue_counts["WARNING"],
                    "errors": issue_counts["ERROR"],
                    "critical": issue_counts["CRITICAL"],
                    "duration_seconds": f"{report.duration_seconds:.6f}",
                },
            )
        )
        logger.info(
            _format_log_section(
                "DATASET",
                {
                    "path": report.dataset_path,
                    "rows": report.rows,
                    "columns": report.columns,
                },
            )
        )
        if report.dataset_version:
            logger.info(
                _format_log_section(
                    "DATASET VERSION",
                    {
                        "metadata_path": report.dataset_version["metadata_path"],
                        "dataset_name": report.dataset_version["dataset_name"],
                        "version": report.dataset_version["version"],
                        "path": report.dataset_version["path"],
                        "schema_path": report.dataset_version["schema_path"],
                    },
                )
            )
        logger.info(
            _format_log_section(
                "SCHEMA",
                {
                    "path": report.schema_path,
                    "version": report.schema_version,
                },
            )
        )
        logger.info(
            _format_log_section(
                "REPORTS",
                {
                    "json": report_paths["json"],
                    "summary": report_paths["summary"],
                },
            )
        )
        if report.issues:
            logger.info(_format_issue_summary(report))
        logger.info("Validation scaffold completed.")
    except (
        ConfigError,
        DataError,
        DatasetRegistryError,
        ValidationError,
        ValidationReportError,
    ) as exc:
        logger.exception("Validation scaffold failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
