"""Tests for V5 pipeline validation ownership."""

from pathlib import Path

import pytest

import app.run_experiments as run_experiments
from app.run_training_pipeline import run_training_pipeline
from app.validation.reports import build_validation_report


@pytest.fixture(autouse=True)
def _silence_training_pipeline_logger(monkeypatch):
    monkeypatch.setattr(
        "app.run_training_pipeline.get_logger",
        lambda *args, **kwargs: _SilentLogger(),
    )


def test_experiment_workflow_validates_when_standalone(monkeypatch, tmp_path):
    validation_calls = []
    _patch_experiment_workflow_dependencies(monkeypatch, validation_calls)
    config_path = _write_test_config(tmp_path)

    run_experiments.run_experiment_workflow(
        config_path,
        validate_before_run=True,
    )

    assert len(validation_calls) == 1


def test_experiment_workflow_can_skip_validation_for_pipeline(monkeypatch, tmp_path):
    validation_calls = []
    _patch_experiment_workflow_dependencies(monkeypatch, validation_calls)
    config_path = _write_test_config(tmp_path)

    run_experiments.run_experiment_workflow(
        config_path,
        validate_before_run=False,
    )

    assert validation_calls == []


def test_training_pipeline_runs_validation_once(tmp_path):
    validation_calls = []
    experiment_calls = []
    config_path = _write_test_config(tmp_path)

    def validation_runner(config_path, schema_path):
        validation_calls.append((config_path, schema_path))
        return _validation_report()

    def experiment_runner(config_path, validate_before_run):
        experiment_calls.append(
            {
                "config_path": config_path,
                "validate_before_run": validate_before_run,
            }
        )
        return _champion_report()

    metadata = run_training_pipeline(
        config_path=config_path,
        pipeline_run_id="pipeline_validation_owner",
        output_dir=tmp_path / "pipeline_runs",
        validation_runner=validation_runner,
        experiment_runner=experiment_runner,
    )

    assert len(validation_calls) == 1
    assert experiment_calls == [
        {
            "config_path": config_path,
            "validate_before_run": False,
        }
    ]
    assert metadata["stage_statuses"] == {
        "validation": "passed",
        "experiments": "passed",
    }


def _patch_experiment_workflow_dependencies(monkeypatch, validation_calls):
    def validation_runner(config_path, schema_path):
        validation_calls.append((config_path, schema_path))
        return _validation_report()

    monkeypatch.setattr(
        run_experiments,
        "validate_dataset_readiness",
        validation_runner,
    )
    monkeypatch.setattr(
        run_experiments,
        "load_experiment_candidates",
        lambda config: [{"name": "candidate", "model": {"type": "decision_tree"}}],
    )
    monkeypatch.setattr(run_experiments, "_build_dataset_context", lambda config: {})
    monkeypatch.setattr(
        run_experiments,
        "_run_candidate",
        lambda config, dataset_context, candidate, logger: _candidate_run(),
    )
    monkeypatch.setattr(
        run_experiments,
        "clear_champion_tags",
        lambda config: 0,
    )
    monkeypatch.setattr(
        run_experiments,
        "set_run_tags",
        lambda config, run_id, tags: None,
    )
    monkeypatch.setattr(
        run_experiments,
        "save_json",
        lambda data, path: None,
    )


def _validation_report():
    return build_validation_report(
        dataset_path="data/churn.csv",
        schema_path="schema_versions/customer_churn_v1.yaml",
        schema_version="v1",
        rows=20,
        columns=9,
        dataset_version={
            "dataset_name": "customer_churn",
            "version": "v1",
            "path": "data/churn.csv",
            "schema_path": "schema_versions/customer_churn_v1.yaml",
            "checksum": {"algorithm": "sha256", "value": "abc123"},
        },
    )


def _candidate_run():
    return {
        "run_id": "run-tree",
        "candidate_name": "decision_tree_baseline",
        "model_type": "decision_tree",
        "status": "FINISHED",
        "dataset_name": "customer_churn",
        "dataset_version": "v1",
        "dataset_checksum": "abc123",
        "pipeline_version": "v5-c4",
        "metrics": {
            "accuracy": 1.0,
            "precision": 1.0,
            "recall": 1.0,
            "f1": 1.0,
            "training_duration_seconds": 0.1,
            "evaluation_duration_seconds": 0.1,
        },
        "artifacts": {
            "model": "model.pkl",
            "metrics": "metrics.json",
            "confusion_matrix": "confusion_matrix.json",
            "config_snapshot": "config_snapshot.json",
            "metadata": "training_metadata.json",
        },
    }


def _champion_report():
    return {
        "champion": {"run_id": "run-tree"},
        "eligible_runs": [{"run_id": "run-tree"}],
        "rejected_runs": [],
    }


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
