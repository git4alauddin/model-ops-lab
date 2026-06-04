"""Tests for V5 pipeline stage task helpers."""

from pathlib import Path

import app.run_training_pipeline as training_pipeline
from app.tasks.experiment_task import (
    ExperimentStageError,
    extract_champion_run_id,
    extract_mlflow_run_ids,
    run_experiment_stage,
    validate_champion_report,
)
from app.tasks.validation_task import run_validation_stage
from app.train import ValidationGateError
from app.validation.reports import ValidationIssue, build_validation_report


def test_validation_stage_runs_runner_and_enforces_gate():
    calls = []

    def validation_runner(config_path, schema_path):
        calls.append((config_path, schema_path))
        return _validation_report(status="passed")

    report = run_validation_stage(
        config_path=Path("configs/training.yaml"),
        schema_path=Path("schema_versions/customer_churn_v1.yaml"),
        validation_runner=validation_runner,
    )

    assert calls == [
        (
            Path("configs/training.yaml"),
            Path("schema_versions/customer_churn_v1.yaml"),
        )
    ]
    assert report.status == "passed"


def test_validation_stage_blocks_failed_validation_report():
    def validation_runner(config_path, schema_path):
        return _validation_report(status="failed")

    try:
        run_validation_stage(
            config_path=Path("configs/training.yaml"),
            schema_path=Path("schema_versions/customer_churn_v1.yaml"),
            validation_runner=validation_runner,
        )
    except ValidationGateError as exc:
        assert "validation status is failed" in str(exc)
    else:
        raise AssertionError("Expected ValidationGateError for failed validation.")


def test_experiment_stage_runs_without_inner_validation():
    calls = []

    def experiment_runner(config_path, validate_before_run):
        calls.append(
            {
                "config_path": config_path,
                "validate_before_run": validate_before_run,
            }
        )
        return _champion_report()

    champion_report = run_experiment_stage(
        config_path=Path("configs/training.yaml"),
        experiment_runner=experiment_runner,
    )

    assert calls == [
        {
            "config_path": Path("configs/training.yaml"),
            "validate_before_run": False,
        }
    ]
    assert champion_report["champion"]["run_id"] == "run-tree"


def test_experiment_stage_wraps_system_exit_failure():
    def experiment_runner(config_path, validate_before_run):
        raise SystemExit(1)

    try:
        run_experiment_stage(
            config_path=Path("configs/training.yaml"),
            experiment_runner=experiment_runner,
        )
    except ExperimentStageError as exc:
        assert "exited with code 1" in str(exc)
    else:
        raise AssertionError("Expected ExperimentStageError for SystemExit failure.")


def test_champion_report_helpers_stay_deterministic():
    champion_report = _champion_report()

    assert validate_champion_report(champion_report) == champion_report
    assert extract_champion_run_id(champion_report) == "run-tree"
    assert extract_mlflow_run_ids(champion_report) == [
        "run-logreg",
        "run-tree",
        "run-forest",
    ]


def test_training_pipeline_delegates_to_stage_helpers(monkeypatch, tmp_path):
    calls = []
    config_path = _write_test_config(tmp_path)

    monkeypatch.setattr(
        training_pipeline,
        "get_logger",
        lambda *args, **kwargs: _SilentLogger(),
    )

    def fake_validation_stage(config_path, schema_path, validation_runner):
        calls.append(("validation", config_path, schema_path))
        return _validation_report(status="passed")

    def fake_experiment_stage(config_path, experiment_runner):
        calls.append(("experiments", config_path))
        return _champion_report()

    monkeypatch.setattr(
        training_pipeline,
        "run_validation_stage",
        fake_validation_stage,
    )
    monkeypatch.setattr(
        training_pipeline,
        "run_experiment_stage",
        fake_experiment_stage,
    )

    metadata = training_pipeline.run_training_pipeline(
        config_path=config_path,
        pipeline_run_id="pipeline_stage_boundary",
        output_dir=tmp_path / "pipeline_runs",
    )

    assert calls == [
        ("validation", config_path, Path("schema_versions/customer_churn_v1.yaml")),
        ("experiments", config_path),
    ]
    assert metadata["status"] == "passed"
    assert metadata["stage_statuses"] == {
        "validation": "passed",
        "experiments": "passed",
    }


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
