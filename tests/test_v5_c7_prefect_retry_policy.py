"""Tests for V5 Prefect retry policy."""

import app.orchestration.prefect_pipeline as prefect_pipeline


def test_validation_stage_task_has_retry_policy():
    task = prefect_pipeline.validation_stage_task

    assert task.retries == prefect_pipeline.PIPELINE_TASK_RETRIES
    assert task.retry_delay_seconds == (
        prefect_pipeline.PIPELINE_TASK_RETRY_DELAY_SECONDS
    )
    assert task.retries == 2
    assert task.retry_delay_seconds == 5


def test_experiment_stage_task_does_not_retry_candidate_runs():
    task = prefect_pipeline.experiment_stage_task

    assert task.retries == 0
