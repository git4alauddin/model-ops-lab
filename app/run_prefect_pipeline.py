"""Command entrypoint for the local Prefect training pipeline."""

from pathlib import Path
from typing import Any, Callable

from app.orchestration.prefect_pipeline import training_pipeline_flow
from app.utils.logger import get_logger
from app.validate_data import DEFAULT_CONFIG_PATH

LOGGER_NAME = "modelopslab.prefect_pipeline"


class PrefectPipelineError(ValueError):
    """Raised when the local Prefect pipeline command fails."""

    def __init__(
        self,
        message: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.metadata = metadata
        self.pipeline_run_id = _metadata_value(metadata, "pipeline_run_id")
        self.failed_stage = _metadata_value(metadata, "failed_stage")


def run_prefect_pipeline(
    *,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    flow_runner: Callable[..., dict[str, Any]] = training_pipeline_flow,
) -> dict[str, Any]:
    """Run the local Prefect flow and return pipeline metadata."""
    try:
        return flow_runner(config_path)
    except Exception as exc:
        metadata = _extract_failure_metadata(exc)
        message = _build_prefect_failure_message(metadata)
        raise PrefectPipelineError(message, metadata=metadata) from exc


def main() -> None:
    """Run the local Prefect training pipeline from the command line."""
    logger = get_logger(LOGGER_NAME)
    try:
        metadata = run_prefect_pipeline()
    except PrefectPipelineError as exc:
        logger.exception(
            "Prefect training pipeline command failed. "
            "pipeline_run_id=%s failed_stage=%s error=%s",
            exc.pipeline_run_id,
            exc.failed_stage,
            exc,
        )
        raise SystemExit(1) from exc

    logger.info(
        "Prefect training pipeline completed. pipeline_run_id=%s champion_run_id=%s",
        metadata["pipeline_run_id"],
        metadata["champion_run_id"],
    )


def _build_prefect_failure_message(metadata: dict[str, Any] | None) -> str:
    pipeline_run_id = _metadata_value(metadata, "pipeline_run_id")
    failed_stage = _metadata_value(metadata, "failed_stage")
    if pipeline_run_id and failed_stage:
        return (
            "Prefect training pipeline failed. "
            f"pipeline_run_id={pipeline_run_id} failed_stage={failed_stage}."
        )
    return "Prefect training pipeline failed."


def _extract_failure_metadata(exc: BaseException) -> dict[str, Any] | None:
    current: BaseException | None = exc
    visited: set[int] = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        metadata = getattr(current, "metadata", None)
        if isinstance(metadata, dict):
            return metadata
        current = current.__cause__ or current.__context__
    return None


def _metadata_value(metadata: dict[str, Any] | None, key: str) -> str | None:
    if not isinstance(metadata, dict):
        return None
    value = metadata.get(key)
    if isinstance(value, str):
        return value
    return None


if __name__ == "__main__":
    main()
