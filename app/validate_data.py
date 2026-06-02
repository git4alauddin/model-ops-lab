"""V2 validation entrypoint for dataset readiness checks."""

from pathlib import Path
from typing import Any, cast

from app.config import ConfigError, load_config
from app.data import DataError, load_dataset
from app.utils.logger import build_log_path, get_logger
from app.validation.checks import ValidationError, load_validation_schema
from app.validation.reports import ValidationReport, build_validation_report

LOGGER_NAME = "modelopslab.validation"
DEFAULT_CONFIG_PATH = Path("configs/training.yaml")
DEFAULT_SCHEMA_PATH = Path("schema_versions/customer_churn_v1.yaml")


def validate_dataset_readiness(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
) -> ValidationReport:
    """Load validation inputs and return the initial dataset readiness report."""
    resolved_config_path = Path(config_path)
    resolved_schema_path = Path(schema_path)
    config = load_config(resolved_config_path)
    schema = load_validation_schema(resolved_schema_path)
    dataset_config = cast(dict[str, Any], config["dataset"])
    dataset_path = _resolve_project_path(
        resolved_config_path,
        cast(str, dataset_config["path"]),
    )
    dataframe = load_dataset(dataset_path)

    return build_validation_report(
        dataset_path=str(dataset_path),
        schema_path=str(resolved_schema_path),
        schema_version=cast(str, schema["version"]),
        rows=len(dataframe),
        columns=len(dataframe.columns),
    )


def _resolve_project_path(config_path: Path, configured_path: str) -> Path:
    path = Path(configured_path)
    if path.is_absolute():
        return path

    project_root = config_path.parent.parent
    return project_root / path


def main() -> None:
    """Run the V2 validation scaffold from the command line."""
    logger = get_logger(LOGGER_NAME)

    try:
        config = load_config(DEFAULT_CONFIG_PATH)
        log_path = build_log_path(config)
        logger = get_logger(LOGGER_NAME, log_path)
        report = validate_dataset_readiness(DEFAULT_CONFIG_PATH, DEFAULT_SCHEMA_PATH)
        logger.info("Validation scaffold completed: %s", report.to_dict())
    except (ConfigError, DataError, ValidationError) as exc:
        logger.exception("Validation scaffold failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
