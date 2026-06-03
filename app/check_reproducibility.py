"""V3 reproducibility check command."""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.config import ConfigError, load_config
from app.dataset_registry import (
    calculate_file_checksum,
    DatasetRegistryError,
    load_dataset_version_metadata,
    resolve_dataset_version_metadata_path,
    validate_dataset_checksum,
)
from app.utils.logger import build_log_path, get_logger

LOGGER_NAME = "modelopslab.reproducibility"
DEFAULT_CONFIG_PATH = Path("configs/training.yaml")


@dataclass(frozen=True)
class ReproducibilityResult:
    """Result of checking the local dataset against registry metadata."""

    status: str
    metadata_path: str
    dataset_name: str
    version: str
    dataset_path: str
    checksum_algorithm: str
    expected_checksum: str
    actual_checksum: str


def check_reproducibility(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> ReproducibilityResult:
    """Verify that the configured dataset file matches its registry checksum."""
    resolved_config_path = Path(config_path)
    config = load_config(resolved_config_path)
    metadata_path = resolve_dataset_version_metadata_path(config)
    metadata = load_dataset_version_metadata(metadata_path)
    project_root = resolved_config_path.parent.parent

    validate_dataset_checksum(metadata, project_root)

    checksum = metadata["checksum"]
    dataset_path = Path(str(metadata["path"]))
    if not dataset_path.is_absolute():
        dataset_path = project_root / dataset_path

    checksum_algorithm = str(checksum["algorithm"])
    return ReproducibilityResult(
        status="passed",
        metadata_path=str(metadata_path),
        dataset_name=str(metadata["dataset_name"]),
        version=str(metadata["version"]),
        dataset_path=str(dataset_path),
        checksum_algorithm=checksum_algorithm,
        expected_checksum=str(checksum["value"]).lower(),
        actual_checksum=calculate_file_checksum(dataset_path, checksum_algorithm),
    )


def _format_log_section(title: str, values: dict[str, object]) -> str:
    """Format a readable key-value section for runtime logs."""
    key_width = max(len(key) for key in values)
    lines = [f"[{title}]"]
    lines.extend(f"{key:<{key_width}} : {value}" for key, value in values.items())
    return "\n".join(lines)


def main() -> None:
    """Run the V3 reproducibility check from the command line."""
    logger = get_logger(LOGGER_NAME)

    try:
        config = load_config(DEFAULT_CONFIG_PATH)
        log_path = build_log_path(config)
        logger = get_logger(LOGGER_NAME, log_path)
        run_started_at = datetime.now(UTC).isoformat()
        logger.info(
            "===== RUN STARTED %s | workflow=reproducibility =====",
            run_started_at,
        )
        result = check_reproducibility(DEFAULT_CONFIG_PATH)
        logger.info(_format_log_section("RUNTIME", {"log_file": log_path}))
        logger.info(
            _format_log_section(
                "REPRODUCIBILITY",
                {
                    "status": result.status,
                    "dataset_name": result.dataset_name,
                    "version": result.version,
                    "metadata_path": result.metadata_path,
                    "dataset_path": result.dataset_path,
                    "checksum_algorithm": result.checksum_algorithm,
                    "expected_checksum": result.expected_checksum,
                    "actual_checksum": result.actual_checksum,
                },
            )
        )
        logger.info("Reproducibility check completed.")
    except (ConfigError, DatasetRegistryError) as exc:
        logger.exception("Reproducibility check failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
