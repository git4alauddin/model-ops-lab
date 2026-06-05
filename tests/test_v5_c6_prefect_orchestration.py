"""Tests for the V5 local Prefect orchestration wrapper."""

from pathlib import Path

import app.orchestration.prefect_pipeline as prefect_pipeline
from app.run_prefect_pipeline import PrefectPipelineError, run_prefect_pipeline


def test_training_pipeline_flow_runs_stage_level_tasks(monkeypatch):
    calls = []

    def fake_initialize(config_path):
        calls.append(("initialize", config_path))
        return {"metadata": {"pipeline_run_id": "pipeline-prefect-test"}}

    def fake_validation(context):
        calls.append(("validation", context["metadata"]["pipeline_run_id"]))
        return context

    def fake_experiment(context):
        calls.append(("experiments", context["metadata"]["pipeline_run_id"]))
        context = dict(context)
        context["mlflow_run_ids"] = ["run-logreg", "run-tree"]
        context["champion_run_id"] = "run-tree"
        return context

    def fake_finalize(context):
        calls.append(("finalize", context["champion_run_id"]))
        return _pipeline_metadata()

    monkeypatch.setattr(prefect_pipeline, "initialize_pipeline_run_task", fake_initialize)
    monkeypatch.setattr(prefect_pipeline, "validation_stage_task", fake_validation)
    monkeypatch.setattr(prefect_pipeline, "experiment_stage_task", fake_experiment)
    monkeypatch.setattr(prefect_pipeline, "finalize_pipeline_run_task", fake_finalize)

    metadata = prefect_pipeline.training_pipeline_flow.fn(
        Path("configs/training.yaml")
    )

    assert calls == [
        ("initialize", Path("configs/training.yaml")),
        ("validation", "pipeline-prefect-test"),
        ("experiments", "pipeline-prefect-test"),
        ("finalize", "run-tree"),
    ]
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
        "pipeline_version": "v5-c11",
        "status": "passed",
        "stage_statuses": {
            "validation": "passed",
            "experiments": "passed",
        },
        "mlflow_run_ids": ["run-logreg", "run-tree"],
        "champion_run_id": "run-tree",
    }
