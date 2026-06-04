"""Tests for V5 Prefect failure visibility."""

from pathlib import Path

from app.run_prefect_pipeline import PrefectPipelineError, run_prefect_pipeline
from app.run_training_pipeline import TrainingPipelineError, run_training_pipeline
from app.validation.reports import ValidationIssue, build_validation_report


def test_training_pipeline_error_exposes_failed_metadata(tmp_path, monkeypatch):
    config_path = _write_test_config(tmp_path)
    monkeypatch.setattr(
        "app.run_training_pipeline.get_logger",
        lambda *args, **kwargs: _SilentLogger(),
    )

    def validation_runner(config_path, schema_path):
        return build_validation_report(
            dataset_path="data/churn.csv",
            schema_path=schema_path,
            schema_version="v1",
            rows=20,
            columns=9,
            issues=[
                ValidationIssue(
                    severity="ERROR",
                    check="schema",
                    message="missing required column",
                )
            ],
        )

    def experiment_runner(config_path, validate_before_run):
        raise AssertionError("Experiment stage should not run after validation failure.")

    try:
        run_training_pipeline(
            config_path=config_path,
            pipeline_run_id="pipeline_test_visible_failure",
            output_dir=tmp_path / "pipeline_runs",
            validation_runner=validation_runner,
            experiment_runner=experiment_runner,
        )
    except TrainingPipelineError as exc:
        assert exc.pipeline_run_id == "pipeline_test_visible_failure"
        assert exc.failed_stage == "validation"
        assert exc.metadata is not None
        assert exc.metadata["status"] == "failed"
        assert exc.metadata["stage_statuses"] == {"validation": "failed"}
    else:
        raise AssertionError("Expected TrainingPipelineError for validation failure.")


def test_prefect_pipeline_error_preserves_nested_pipeline_failure_metadata():
    metadata = {
        "pipeline_run_id": "pipeline_prefect_visible_failure",
        "status": "failed",
        "failed_stage": "experiments",
    }

    def failing_flow_runner(config_path):
        try:
            raise TrainingPipelineError(
                "Training pipeline failed at stage experiments.",
                metadata=metadata,
            )
        except TrainingPipelineError as exc:
            raise RuntimeError("Prefect flow failed.") from exc

    try:
        run_prefect_pipeline(
            config_path=Path("configs/training.yaml"),
            flow_runner=failing_flow_runner,
        )
    except PrefectPipelineError as exc:
        assert exc.metadata == metadata
        assert exc.pipeline_run_id == "pipeline_prefect_visible_failure"
        assert exc.failed_stage == "experiments"
        assert (
            "pipeline_run_id=pipeline_prefect_visible_failure failed_stage=experiments"
            in str(exc)
        )
    else:
        raise AssertionError("Expected PrefectPipelineError for failed flow.")


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
