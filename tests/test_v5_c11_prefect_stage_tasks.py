"""Tests for V5 stage-level Prefect tasks."""

from pathlib import Path

import app.orchestration.prefect_pipeline as prefect_pipeline
from app.validation.reports import ValidationIssue, build_validation_report


def test_initialize_pipeline_run_task_persists_running_metadata(tmp_path, monkeypatch):
    config_path = _write_test_config(tmp_path)
    monkeypatch.setattr(
        prefect_pipeline,
        "get_logger",
        lambda *args, **kwargs: _SilentLogger(),
    )

    context = prefect_pipeline.initialize_pipeline_run_task.fn(
        config_path,
        pipeline_run_id="pipeline_stage_prefect",
        output_dir=tmp_path / "pipeline_runs",
    )

    output_path = tmp_path / "pipeline_runs" / "pipeline_stage_prefect.json"
    metadata = _read_json(output_path)
    assert context["metadata"]["pipeline_run_id"] == "pipeline_stage_prefect"
    assert Path(context["validation_schema_path"]) == Path(
        "schema_versions/customer_churn_v1.yaml"
    )
    assert metadata["status"] == "running"


def test_validation_stage_task_updates_metadata(tmp_path, monkeypatch):
    context = _context(tmp_path)

    def fake_validation_stage(config_path, schema_path, validation_runner):
        return _validation_report(status="passed")

    monkeypatch.setattr(prefect_pipeline, "run_validation_stage", fake_validation_stage)

    context = prefect_pipeline.validation_stage_task.fn(context)

    metadata = context["metadata"]
    assert metadata["dataset_version"]["version"] == "v1"
    assert metadata["stage_statuses"] == {"validation": "passed"}
    assert _read_json(_metadata_path(tmp_path))["stage_statuses"] == {
        "validation": "passed",
    }


def test_validation_stage_task_preserves_failed_metadata(tmp_path, monkeypatch):
    context = _context(tmp_path)
    monkeypatch.setattr(
        prefect_pipeline,
        "get_logger",
        lambda *args, **kwargs: _SilentLogger(),
    )

    def fake_validation_stage(config_path, schema_path, validation_runner):
        raise RuntimeError("validation exploded")

    monkeypatch.setattr(prefect_pipeline, "run_validation_stage", fake_validation_stage)

    try:
        prefect_pipeline.validation_stage_task.fn(context)
    except prefect_pipeline.PrefectStageError as exc:
        assert exc.pipeline_run_id == "pipeline_stage_prefect"
        assert exc.failed_stage == "validation"
        assert exc.metadata["status"] == "failed"
    else:
        raise AssertionError("Expected PrefectStageError for validation failure.")

    metadata = _read_json(_metadata_path(tmp_path))
    assert metadata["status"] == "failed"
    assert metadata["failed_stage"] == "validation"


def test_experiment_and_finalize_tasks_complete_metadata(tmp_path, monkeypatch):
    context = _context(tmp_path)
    context["metadata"]["stage_statuses"] = {"validation": "passed"}
    monkeypatch.setattr(
        prefect_pipeline,
        "get_logger",
        lambda *args, **kwargs: _SilentLogger(),
    )

    def fake_experiment_stage(config_path, experiment_runner):
        return _champion_report()

    monkeypatch.setattr(prefect_pipeline, "run_experiment_stage", fake_experiment_stage)

    context = prefect_pipeline.experiment_stage_task.fn(context)
    metadata = prefect_pipeline.finalize_pipeline_run_task.fn(context)

    assert metadata["status"] == "passed"
    assert metadata["stage_statuses"] == {
        "validation": "passed",
        "experiments": "passed",
    }
    assert metadata["mlflow_run_ids"] == ["run-logreg", "run-tree", "run-forest"]
    assert metadata["champion_run_id"] == "run-tree"


def test_finalize_pipeline_run_task_preserves_failed_metadata(tmp_path, monkeypatch):
    context = _context(tmp_path)
    context["metadata"]["stage_statuses"] = {
        "validation": "passed",
        "experiments": "passed",
    }
    monkeypatch.setattr(
        prefect_pipeline,
        "get_logger",
        lambda *args, **kwargs: _SilentLogger(),
    )

    try:
        prefect_pipeline.finalize_pipeline_run_task.fn(context)
    except prefect_pipeline.PrefectStageError as exc:
        assert exc.pipeline_run_id == "pipeline_stage_prefect"
        assert exc.failed_stage == "finalization"
        assert exc.metadata["status"] == "failed"
    else:
        raise AssertionError("Expected PrefectStageError for finalization failure.")

    metadata = _read_json(_metadata_path(tmp_path))
    assert metadata["status"] == "failed"
    assert metadata["failed_stage"] == "finalization"


def _context(tmp_path: Path) -> dict:
    metadata = {
        "pipeline_run_id": "pipeline_stage_prefect",
        "pipeline_version": "v5-c11",
        "started_at": "2026-06-04T00:00:00+00:00",
        "completed_at": None,
        "status": "running",
        "stage_statuses": {},
        "failed_stage": None,
        "dataset_version": None,
        "config_path": str(tmp_path / "training.yaml"),
        "mlflow_run_ids": [],
        "champion_run_id": None,
    }
    output_dir = tmp_path / "pipeline_runs"
    output_dir.mkdir()
    prefect_pipeline.save_pipeline_run_metadata(metadata, output_dir)
    return {
        "metadata": metadata,
        "config_path": str(tmp_path / "training.yaml"),
        "output_dir": str(output_dir),
        "validation_schema_path": "schema_versions/customer_churn_v1.yaml",
        "log_path": None,
    }


def _metadata_path(tmp_path: Path) -> Path:
    return tmp_path / "pipeline_runs" / "pipeline_stage_prefect.json"


def _validation_report(status: str):
    issues = []
    if status == "failed":
        issues.append(
            ValidationIssue(
                severity="ERROR",
                check="schema",
                message="missing required column",
            )
        )

    return build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        issues=issues,
        dataset_version={
            "dataset_name": "customer_churn",
            "version": "v1",
            "path": "data/churn.csv",
            "schema_path": "schema_versions/customer_churn_v1.yaml",
            "checksum": {"algorithm": "sha256", "value": "abc123"},
        },
    )


def _champion_report() -> dict:
    return {
        "champion": {"run_id": "run-tree"},
        "eligible_runs": [
            {"run_id": "run-logreg"},
            {"run_id": "run-tree"},
            {"run_id": "run-forest"},
        ],
        "rejected_runs": [],
    }


def _read_json(path: Path) -> dict:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _write_test_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "training.yaml"
    config_path.write_text(
        "\n".join(
            [
                "dataset:",
                "  path: data/churn.csv",
                "  target_column: churn",
                "training:",
                "  test_size: 0.2",
                "  random_state: 42",
                "logging:",
                f"  dir: '{(tmp_path / 'logs').as_posix()}'",
                "  file: modelopslab.log",
            ]
        ),
        encoding="utf-8",
    )
    return config_path


class _SilentLogger:
    def info(self, *args, **kwargs):
        return None

    def exception(self, *args, **kwargs):
        return None
