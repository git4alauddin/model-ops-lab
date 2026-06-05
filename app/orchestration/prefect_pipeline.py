"""Prefect orchestration wrapper for the V5 training pipeline."""

from pathlib import Path
from typing import Any

from prefect import flow, task

from app.config import load_config
from app.pipeline_run_metadata import (
    DEFAULT_PIPELINE_RUNS_DIR,
    build_pipeline_run_metadata,
    complete_pipeline_run,
    save_pipeline_run_metadata,
    update_stage_status,
)
from app.run_experiments import run_experiment_workflow
from app.run_training_pipeline import EXPERIMENTS_STAGE, LOGGER_NAME, VALIDATION_STAGE
from app.tasks.experiment_task import (
    extract_champion_run_id,
    extract_mlflow_run_ids,
    run_experiment_stage,
)
from app.tasks.validation_task import run_validation_stage
from app.train import resolve_validation_schema_path
from app.utils.logger import build_log_path, get_logger
from app.validate_data import DEFAULT_CONFIG_PATH, validate_dataset_readiness

INITIALIZATION_STAGE = "initialization"
FINALIZATION_STAGE = "finalization"
PIPELINE_TASK_RETRIES = 2
PIPELINE_TASK_RETRY_DELAY_SECONDS = 5


class PrefectStageError(ValueError):
    """Raised when a Prefect pipeline stage fails with persisted metadata."""

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


@task(name="initialize-pipeline-run")
def initialize_pipeline_run_task(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    *,
    pipeline_run_id: str | None = None,
    output_dir: str | Path = DEFAULT_PIPELINE_RUNS_DIR,
) -> dict[str, Any]:
    """Create pipeline metadata and resolve runtime configuration."""
    resolved_config_path = Path(config_path)
    resolved_output_dir = Path(output_dir)
    metadata = build_pipeline_run_metadata(
        pipeline_run_id=pipeline_run_id,
        config_path=resolved_config_path,
    )
    save_pipeline_run_metadata(metadata, resolved_output_dir)
    logger = get_logger(LOGGER_NAME)

    try:
        config = load_config(resolved_config_path)
        log_path = build_log_path(config)
        logger = get_logger(LOGGER_NAME, log_path)
        validation_schema_path = resolve_validation_schema_path(config)
        logger.info(
            "===== PIPELINE RUN STARTED %s =====",
            metadata["pipeline_run_id"],
        )
        return {
            "metadata": metadata,
            "config_path": str(resolved_config_path),
            "output_dir": str(resolved_output_dir),
            "validation_schema_path": str(validation_schema_path),
            "log_path": str(log_path) if log_path is not None else None,
        }
    except Exception as exc:
        failed_metadata = _mark_pipeline_failed(
            metadata,
            INITIALIZATION_STAGE,
            resolved_output_dir,
        )
        logger.exception(
            "Prefect pipeline initialization failed. pipeline_run_id=%s",
            metadata["pipeline_run_id"],
        )
        raise PrefectStageError(
            f"Prefect pipeline failed at stage {INITIALIZATION_STAGE}: {exc}",
            metadata=failed_metadata,
        ) from exc


@task(
    name="validation-stage",
    retries=PIPELINE_TASK_RETRIES,
    retry_delay_seconds=PIPELINE_TASK_RETRY_DELAY_SECONDS,
)
def validation_stage_task(context: dict[str, Any]) -> dict[str, Any]:
    """Run validation as a tracked Prefect task."""
    metadata = context["metadata"]
    output_dir = Path(context["output_dir"])

    try:
        metadata = update_stage_status(metadata, VALIDATION_STAGE, "running")
        save_pipeline_run_metadata(metadata, output_dir)
        validation_report = run_validation_stage(
            config_path=Path(context["config_path"]),
            schema_path=Path(context["validation_schema_path"]),
            validation_runner=validate_dataset_readiness,
        )
        metadata["dataset_version"] = validation_report.dataset_version
        metadata = update_stage_status(metadata, VALIDATION_STAGE, "passed")
        save_pipeline_run_metadata(metadata, output_dir)
        return _update_context(context, metadata=metadata)
    except Exception as exc:
        failed_metadata = _mark_pipeline_failed(metadata, VALIDATION_STAGE, output_dir)
        _log_stage_failure(context, VALIDATION_STAGE, failed_metadata)
        raise PrefectStageError(
            f"Prefect pipeline failed at stage {VALIDATION_STAGE}: {exc}",
            metadata=failed_metadata,
        ) from exc


@task(name="experiment-stage")
def experiment_stage_task(context: dict[str, Any]) -> dict[str, Any]:
    """Run experiments as a tracked Prefect task."""
    metadata = context["metadata"]
    output_dir = Path(context["output_dir"])

    try:
        metadata = update_stage_status(metadata, EXPERIMENTS_STAGE, "running")
        save_pipeline_run_metadata(metadata, output_dir)
        champion_report = run_experiment_stage(
            config_path=Path(context["config_path"]),
            experiment_runner=run_experiment_workflow,
        )
        metadata = update_stage_status(metadata, EXPERIMENTS_STAGE, "passed")
        save_pipeline_run_metadata(metadata, output_dir)
        return _update_context(
            context,
            metadata=metadata,
            mlflow_run_ids=extract_mlflow_run_ids(champion_report),
            champion_run_id=extract_champion_run_id(champion_report),
        )
    except Exception as exc:
        failed_metadata = _mark_pipeline_failed(metadata, EXPERIMENTS_STAGE, output_dir)
        _log_stage_failure(context, EXPERIMENTS_STAGE, failed_metadata)
        raise PrefectStageError(
            f"Prefect pipeline failed at stage {EXPERIMENTS_STAGE}: {exc}",
            metadata=failed_metadata,
        ) from exc


@task(name="finalize-pipeline-run")
def finalize_pipeline_run_task(context: dict[str, Any]) -> dict[str, Any]:
    """Finalize a successful pipeline run."""
    try:
        metadata = complete_pipeline_run(
            context["metadata"],
            status="passed",
            mlflow_run_ids=context["mlflow_run_ids"],
            champion_run_id=context["champion_run_id"],
        )
        save_pipeline_run_metadata(metadata, Path(context["output_dir"]))
        get_logger(LOGGER_NAME, _context_log_path(context)).info(
            "Training pipeline completed. pipeline_run_id=%s champion_run_id=%s",
            metadata["pipeline_run_id"],
            metadata["champion_run_id"],
        )
        return metadata
    except Exception as exc:
        failed_metadata = _mark_pipeline_failed(
            context["metadata"],
            FINALIZATION_STAGE,
            Path(context["output_dir"]),
        )
        _log_stage_failure(context, FINALIZATION_STAGE, failed_metadata)
        raise PrefectStageError(
            f"Prefect pipeline failed at stage {FINALIZATION_STAGE}: {exc}",
            metadata=failed_metadata,
        ) from exc


@flow(name="modelopslab-training-pipeline")
def training_pipeline_flow(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> dict[str, Any]:
    """Run the V5 training pipeline as local stage-level Prefect tasks."""
    context = initialize_pipeline_run_task(config_path)
    context = validation_stage_task(context)
    context = experiment_stage_task(context)
    return finalize_pipeline_run_task(context)


def _mark_pipeline_failed(
    metadata: dict[str, Any],
    failed_stage: str,
    output_dir: Path,
) -> dict[str, Any]:
    failed_metadata = update_stage_status(metadata, failed_stage, "failed")
    failed_metadata = complete_pipeline_run(
        failed_metadata,
        status="failed",
        failed_stage=failed_stage,
    )
    save_pipeline_run_metadata(failed_metadata, output_dir)
    return failed_metadata


def _update_context(context: dict[str, Any], **updates: Any) -> dict[str, Any]:
    updated_context = dict(context)
    updated_context.update(updates)
    return updated_context


def _log_stage_failure(
    context: dict[str, Any],
    failed_stage: str,
    failed_metadata: dict[str, Any],
) -> None:
    get_logger(LOGGER_NAME, _context_log_path(context)).exception(
        "Training pipeline failed at stage %s. pipeline_run_id=%s",
        failed_stage,
        failed_metadata["pipeline_run_id"],
    )


def _context_log_path(context: dict[str, Any]) -> Path | None:
    log_path = context.get("log_path")
    if isinstance(log_path, str):
        return Path(log_path)
    return None


def _metadata_value(metadata: dict[str, Any] | None, key: str) -> str | None:
    if not isinstance(metadata, dict):
        return None
    value = metadata.get(key)
    if isinstance(value, str):
        return value
    return None
