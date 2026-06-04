"""Command entrypoint for the local Prefect training pipeline."""

from pathlib import Path
from typing import Any, Callable

from app.orchestration.prefect_pipeline import training_pipeline_flow
from app.utils.logger import get_logger
from app.validate_data import DEFAULT_CONFIG_PATH

LOGGER_NAME = "modelopslab.prefect_pipeline"


class PrefectPipelineError(ValueError):
    """Raised when the local Prefect pipeline command fails."""


def run_prefect_pipeline(
    *,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    flow_runner: Callable[..., dict[str, Any]] = training_pipeline_flow,
) -> dict[str, Any]:
    """Run the local Prefect flow and return pipeline metadata."""
    try:
        return flow_runner(config_path)
    except Exception as exc:
        raise PrefectPipelineError("Prefect training pipeline failed.") from exc


def main() -> None:
    """Run the local Prefect training pipeline from the command line."""
    logger = get_logger(LOGGER_NAME)
    try:
        metadata = run_prefect_pipeline()
    except PrefectPipelineError as exc:
        logger.exception("Prefect training pipeline command failed: %s", exc)
        raise SystemExit(1) from exc

    logger.info(
        "Prefect training pipeline completed. pipeline_run_id=%s champion_run_id=%s",
        metadata["pipeline_run_id"],
        metadata["champion_run_id"],
    )


if __name__ == "__main__":
    main()
