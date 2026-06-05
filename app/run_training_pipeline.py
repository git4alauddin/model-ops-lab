"""Plain Python V5 training pipeline entrypoint."""

from pathlib import Path
from typing import Any, Callable

from app.config import load_config
from app.pipeline_run_metadata import (
    DEFAULT_PIPELINE_RUNS_DIR,
    PipelineRunMetadataError,
    build_pipeline_run_metadata,
    complete_pipeline_run,
    save_pipeline_run_metadata,
    update_stage_status,
)
from app.run_experiments import run_experiment_workflow
from app.tasks.experiment_task import (
    ExperimentStageError,
    extract_champion_run_id,
    extract_mlflow_run_ids,
    run_experiment_stage,
    validate_champion_report as validate_task_champion_report,
)
from app.tasks.validation_task import run_validation_stage
from app.train import resolve_validation_schema_path
from app.utils.logger import build_log_path, get_logger
from app.validate_data import DEFAULT_CONFIG_PATH, validate_dataset_readiness
from app.validation.reports import ValidationReport

LOGGER_NAME = "modelopslab.training_pipeline"
VALIDATION_STAGE = "validation"
EXPERIMENTS_STAGE = "experiments"


class TrainingPipelineError(ValueError):
    """Raised when the plain Python training pipeline fails."""

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


def validate_champion_report(champion_report: dict[str, Any]) -> dict[str, Any]:
    """Validate and return a champion report for existing pipeline callers."""
    try:
        return validate_task_champion_report(champion_report)
    except ExperimentStageError as exc:
        raise TrainingPipelineError(str(exc)) from exc


def run_training_pipeline(
    *,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    pipeline_run_id: str | None = None,
    output_dir: Path = DEFAULT_PIPELINE_RUNS_DIR,
    validation_runner: Callable[[str | Path, str | Path], ValidationReport] = (
        validate_dataset_readiness
    ),
    experiment_runner: Callable[..., dict[str, Any]] = run_experiment_workflow,
) -> dict[str, Any]:
    """Run validation and multi-model experiments as one controlled pipeline."""
    resolved_config_path = Path(config_path)
    metadata = build_pipeline_run_metadata(
        pipeline_run_id=pipeline_run_id,
        config_path=resolved_config_path,
    )
    save_pipeline_run_metadata(metadata, output_dir)
    current_stage = "initialization"
    logger = get_logger(LOGGER_NAME)

    try:
        config = load_config(resolved_config_path)
        logger = get_logger(LOGGER_NAME, build_log_path(config))
        validation_schema_path = resolve_validation_schema_path(config)
        logger.info(
            "===== PIPELINE RUN STARTED %s =====",
            metadata["pipeline_run_id"],
        )

        current_stage = VALIDATION_STAGE
        metadata = update_stage_status(metadata, current_stage, "running")
        save_pipeline_run_metadata(metadata, output_dir)
        validation_report = run_validation_stage(
            config_path=resolved_config_path,
            schema_path=validation_schema_path,
            validation_runner=validation_runner,
        )
        metadata["dataset_version"] = validation_report.dataset_version
        metadata = update_stage_status(metadata, current_stage, "passed")
        save_pipeline_run_metadata(metadata, output_dir)

        current_stage = EXPERIMENTS_STAGE
        metadata = update_stage_status(metadata, current_stage, "running")
        save_pipeline_run_metadata(metadata, output_dir)
        champion_report = run_experiment_stage(
            config_path=resolved_config_path,
            experiment_runner=experiment_runner,
        )
        metadata = update_stage_status(metadata, current_stage, "passed")
        metadata = complete_pipeline_run(
            metadata,
            status="passed",
            mlflow_run_ids=extract_mlflow_run_ids(champion_report),
            champion_run_id=extract_champion_run_id(champion_report),
        )
        save_pipeline_run_metadata(metadata, output_dir)

        logger.info(
            "Training pipeline completed. pipeline_run_id=%s champion_run_id=%s",
            metadata["pipeline_run_id"],
            metadata["champion_run_id"],
        )
        return metadata
    except Exception as exc:
        failed_metadata = _mark_pipeline_failed(metadata, current_stage)
        save_pipeline_run_metadata(failed_metadata, output_dir)
        logger.exception(
            "Training pipeline failed at stage %s. pipeline_run_id=%s",
            current_stage,
            metadata["pipeline_run_id"],
        )
        raise TrainingPipelineError(
            f"Training pipeline failed at stage {current_stage}: {exc}",
            metadata=failed_metadata,
        ) from exc


def main() -> None:
    """Run the V5 plain Python training pipeline from the command line."""
    try:
        run_training_pipeline()
    except (PipelineRunMetadataError, TrainingPipelineError) as exc:
        logger = get_logger(LOGGER_NAME)
        logger.error("Training pipeline command failed: %s", exc)
        raise SystemExit(1) from exc


def _mark_pipeline_failed(
    metadata: dict[str, Any],
    failed_stage: str,
) -> dict[str, Any]:
    failed_metadata = update_stage_status(metadata, failed_stage, "failed")
    return complete_pipeline_run(
        failed_metadata,
        status="failed",
        failed_stage=failed_stage,
    )


def _metadata_value(metadata: dict[str, Any] | None, key: str) -> str | None:
    if not isinstance(metadata, dict):
        return None
    value = metadata.get(key)
    if isinstance(value, str):
        return value
    return None


if __name__ == "__main__":
    main()
