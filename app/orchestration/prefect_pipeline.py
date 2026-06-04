"""Prefect orchestration wrapper for the V5 training pipeline."""

from pathlib import Path
from typing import Any

from prefect import flow, task

from app.validate_data import DEFAULT_CONFIG_PATH

PIPELINE_TASK_RETRIES = 2
PIPELINE_TASK_RETRY_DELAY_SECONDS = 5


@task(
    name="run-training-pipeline",
    retries=PIPELINE_TASK_RETRIES,
    retry_delay_seconds=PIPELINE_TASK_RETRY_DELAY_SECONDS,
)
def run_training_pipeline_task(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> dict[str, Any]:
    """Run the existing plain Python training pipeline inside a Prefect task."""
    from app.run_training_pipeline import run_training_pipeline

    return run_training_pipeline(config_path=config_path)


@flow(name="modelopslab-training-pipeline")
def training_pipeline_flow(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> dict[str, Any]:
    """Run the V5 training pipeline as a local Prefect flow."""
    return run_training_pipeline_task(config_path)
