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
from app.train import enforce_validation_gate, resolve_validation_schema_path
from app.utils.logger import build_log_path, get_logger
from app.validate_data import DEFAULT_CONFIG_PATH, validate_dataset_readiness
from app.validation.reports import ValidationReport

LOGGER_NAME = "modelopslab.training_pipeline"
VALIDATION_STAGE = "validation"
EXPERIMENTS_STAGE = "experiments"


class TrainingPipelineError(ValueError):
    """Raised when the plain Python training pipeline fails."""


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
        validation_report = validation_runner(
            resolved_config_path,
            validation_schema_path,
        )
        metadata["dataset_version"] = validation_report.dataset_version
        enforce_validation_gate(validation_report)
        metadata = update_stage_status(metadata, current_stage, "passed")
        save_pipeline_run_metadata(metadata, output_dir)

        current_stage = EXPERIMENTS_STAGE
        metadata = update_stage_status(metadata, current_stage, "running")
        save_pipeline_run_metadata(metadata, output_dir)
        champion_report = _run_experiments(
            experiment_runner,
            resolved_config_path,
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
            f"Training pipeline failed at stage {current_stage}: {exc}"
        ) from exc


def extract_champion_run_id(champion_report: dict[str, Any]) -> str:
    """Return the champion MLflow run ID from a champion report."""
    champion = champion_report["champion"]
    return str(champion["run_id"])


def extract_mlflow_run_ids(champion_report: dict[str, Any]) -> list[str]:
    """Return unique MLflow run IDs from eligible runs and the champion."""
    run_ids = []
    for run in champion_report.get("eligible_runs", []):
        if isinstance(run, dict) and isinstance(run.get("run_id"), str):
            run_ids.append(run["run_id"])
    run_ids.append(extract_champion_run_id(champion_report))
    return list(dict.fromkeys(run_ids))


def main() -> None:
    """Run the V5 plain Python training pipeline from the command line."""
    try:
        run_training_pipeline()
    except (PipelineRunMetadataError, TrainingPipelineError) as exc:
        logger = get_logger(LOGGER_NAME)
        logger.error("Training pipeline command failed: %s", exc)
        raise SystemExit(1) from exc


def _run_experiments(
    experiment_runner: Callable[..., dict[str, Any]],
    config_path: Path,
) -> dict[str, Any]:
    try:
        champion_report = experiment_runner(
            config_path,
            validate_before_run=False,
        )
    except SystemExit as exc:
        if exc.code in (None, 0):
            raise TrainingPipelineError(
                "Experiment runner exited without a champion report."
            ) from exc
        raise TrainingPipelineError(
            f"Experiment runner exited with code {exc.code}."
        ) from exc
    return validate_champion_report(champion_report)


def validate_champion_report(champion_report: dict[str, Any]) -> dict[str, Any]:
    """Validate and return a champion report dictionary."""
    if not isinstance(champion_report, dict):
        raise TrainingPipelineError("Experiment runner must return a champion report.")

    champion = champion_report.get("champion")
    if not isinstance(champion, dict) or not isinstance(champion.get("run_id"), str):
        raise TrainingPipelineError("Champion report requires champion.run_id.")

    eligible_runs = champion_report.get("eligible_runs")
    if not isinstance(eligible_runs, list):
        raise TrainingPipelineError("Champion report requires eligible_runs.")

    return champion_report


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


if __name__ == "__main__":
    main()
