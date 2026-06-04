"""Tests for V5 Prefect retry policy."""

from pathlib import Path

import app.orchestration.prefect_pipeline as prefect_pipeline


def test_training_pipeline_task_has_retry_policy():
    task = prefect_pipeline.run_training_pipeline_task

    assert task.retries == prefect_pipeline.PIPELINE_TASK_RETRIES
    assert task.retry_delay_seconds == (
        prefect_pipeline.PIPELINE_TASK_RETRY_DELAY_SECONDS
    )
    assert task.retries == 2
    assert task.retry_delay_seconds == 5


def test_training_pipeline_task_still_delegates_to_plain_pipeline(monkeypatch):
    calls = []

    def fake_run_training_pipeline(config_path):
        calls.append(config_path)
        return {"pipeline_run_id": "pipeline-retry-test", "status": "passed"}

    monkeypatch.setattr(
        "app.run_training_pipeline.run_training_pipeline",
        fake_run_training_pipeline,
    )

    metadata = prefect_pipeline.run_training_pipeline_task.fn(
        Path("configs/training.yaml")
    )

    assert calls == [Path("configs/training.yaml")]
    assert metadata["pipeline_run_id"] == "pipeline-retry-test"
