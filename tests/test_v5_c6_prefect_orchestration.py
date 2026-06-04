"""Tests for the V5 local Prefect orchestration wrapper."""

from pathlib import Path

import app.orchestration.prefect_pipeline as prefect_pipeline
from app.run_prefect_pipeline import PrefectPipelineError, run_prefect_pipeline


def test_training_pipeline_task_delegates_to_plain_pipeline(monkeypatch):
    calls = []

    def fake_run_training_pipeline(config_path):
        calls.append(config_path)
        return _pipeline_metadata()

    monkeypatch.setattr(
        "app.run_training_pipeline.run_training_pipeline",
        fake_run_training_pipeline,
    )

    metadata = prefect_pipeline.run_training_pipeline_task.fn(
        Path("configs/training.yaml")
    )

    assert calls == [Path("configs/training.yaml")]
    assert metadata["pipeline_run_id"] == "pipeline-prefect-test"


def test_training_pipeline_flow_delegates_to_prefect_task(monkeypatch):
    calls = []

    def fake_task(config_path):
        calls.append(config_path)
        return _pipeline_metadata()

    monkeypatch.setattr(prefect_pipeline, "run_training_pipeline_task", fake_task)

    metadata = prefect_pipeline.training_pipeline_flow.fn(
        Path("configs/training.yaml")
    )

    assert calls == [Path("configs/training.yaml")]
    assert metadata["champion_run_id"] == "run-tree"


def test_run_prefect_pipeline_calls_flow_runner():
    calls = []

    def fake_flow_runner(config_path):
        calls.append(config_path)
        return _pipeline_metadata()

    metadata = run_prefect_pipeline(
        config_path=Path("configs/training.yaml"),
        flow_runner=fake_flow_runner,
    )

    assert calls == [Path("configs/training.yaml")]
    assert metadata["status"] == "passed"


def test_run_prefect_pipeline_wraps_flow_errors():
    def failing_flow_runner(config_path):
        raise RuntimeError("flow failed")

    try:
        run_prefect_pipeline(flow_runner=failing_flow_runner)
    except PrefectPipelineError as exc:
        assert "Prefect training pipeline failed" in str(exc)
    else:
        raise AssertionError("Expected PrefectPipelineError for failed flow.")


def _pipeline_metadata() -> dict:
    return {
        "pipeline_run_id": "pipeline-prefect-test",
        "pipeline_version": "v5-c10",
        "status": "passed",
        "stage_statuses": {
            "validation": "passed",
            "experiments": "passed",
        },
        "mlflow_run_ids": ["run-logreg", "run-tree"],
        "champion_run_id": "run-tree",
    }
