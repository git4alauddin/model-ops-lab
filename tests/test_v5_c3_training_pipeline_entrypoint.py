"""Tests for the V5 plain Python training pipeline entrypoint."""

from pathlib import Path

from app.run_training_pipeline import (
    TrainingPipelineError,
    extract_champion_run_id,
    extract_mlflow_run_ids,
    run_training_pipeline,
    validate_champion_report,
)
from app.validation.reports import (
    ValidationIssue,
    build_validation_report,
)


def test_run_training_pipeline_persists_success_metadata(tmp_path):
    experiment_calls = []
    config_path = _write_test_config(tmp_path)

    def validation_runner(config_path, schema_path):
        assert config_path == tmp_path / "training.yaml"
        assert schema_path == Path("schema_versions/customer_churn_v1.yaml")
        return _validation_report(status="passed")

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
        pipeline_run_id="pipeline_test_success",
        output_dir=tmp_path / "pipeline_runs",
        validation_runner=validation_runner,
        experiment_runner=experiment_runner,
    )

    output_path = tmp_path / "pipeline_runs" / "pipeline_test_success.json"
    assert output_path.exists()
    assert experiment_calls == [
        {
            "config_path": config_path,
            "validate_before_run": False,
        }
    ]
    assert metadata["status"] == "passed"
    assert metadata["stage_statuses"] == {
        "validation": "passed",
        "experiments": "passed",
    }
    assert metadata["dataset_version"]["version"] == "v1"
    assert metadata["mlflow_run_ids"] == ["run-logreg", "run-tree", "run-forest"]
    assert metadata["champion_run_id"] == "run-tree"


def test_run_training_pipeline_records_validation_failure(tmp_path):
    experiment_called = False
    config_path = _write_test_config(tmp_path)

    def validation_runner(config_path, schema_path):
        return _validation_report(status="failed")

    def experiment_runner(config_path, validate_before_run):
        nonlocal experiment_called
        experiment_called = True
        return _champion_report()

    try:
        run_training_pipeline(
            config_path=config_path,
            pipeline_run_id="pipeline_test_validation_failure",
            output_dir=tmp_path / "pipeline_runs",
            validation_runner=validation_runner,
            experiment_runner=experiment_runner,
        )
    except TrainingPipelineError as exc:
        assert "validation" in str(exc)
    else:
        raise AssertionError("Expected TrainingPipelineError for validation failure.")

    output_path = tmp_path / "pipeline_runs" / "pipeline_test_validation_failure.json"
    metadata = _read_json(output_path)
    assert experiment_called is False
    assert metadata["status"] == "failed"
    assert metadata["failed_stage"] == "validation"
    assert metadata["stage_statuses"] == {"validation": "failed"}


def test_run_training_pipeline_records_experiment_failure(tmp_path):
    config_path = _write_test_config(tmp_path)

    def validation_runner(config_path, schema_path):
        return _validation_report(status="passed")

    def experiment_runner(config_path, validate_before_run):
        assert validate_before_run is False
        raise RuntimeError("candidate run failed")

    try:
        run_training_pipeline(
            config_path=config_path,
            pipeline_run_id="pipeline_test_experiment_failure",
            output_dir=tmp_path / "pipeline_runs",
            validation_runner=validation_runner,
            experiment_runner=experiment_runner,
        )
    except TrainingPipelineError as exc:
        assert "experiments" in str(exc)
    else:
        raise AssertionError("Expected TrainingPipelineError for experiment failure.")

    output_path = tmp_path / "pipeline_runs" / "pipeline_test_experiment_failure.json"
    metadata = _read_json(output_path)
    assert metadata["status"] == "failed"
    assert metadata["failed_stage"] == "experiments"
    assert metadata["stage_statuses"] == {
        "validation": "passed",
        "experiments": "failed",
    }


def test_run_training_pipeline_records_experiment_system_exit_failure(tmp_path):
    config_path = _write_test_config(tmp_path)

    def validation_runner(config_path, schema_path):
        return _validation_report(status="passed")

    def experiment_runner(config_path, validate_before_run):
        assert validate_before_run is False
        raise SystemExit(1)

    try:
        run_training_pipeline(
            config_path=config_path,
            pipeline_run_id="pipeline_test_system_exit_failure",
            output_dir=tmp_path / "pipeline_runs",
            validation_runner=validation_runner,
            experiment_runner=experiment_runner,
        )
    except TrainingPipelineError as exc:
        assert "experiments" in str(exc)
    else:
        raise AssertionError("Expected TrainingPipelineError for SystemExit failure.")

    output_path = tmp_path / "pipeline_runs" / "pipeline_test_system_exit_failure.json"
    metadata = _read_json(output_path)
    assert metadata["failed_stage"] == "experiments"


def test_extract_champion_and_mlflow_run_ids_from_champion_report():
    champion_report = _champion_report()

    assert extract_champion_run_id(champion_report) == "run-tree"
    assert extract_mlflow_run_ids(champion_report) == [
        "run-logreg",
        "run-tree",
        "run-forest",
    ]


def test_validate_champion_report_rejects_missing_eligible_runs():
    try:
        validate_champion_report({"champion": {"run_id": "run-tree"}})
    except TrainingPipelineError as exc:
        assert "eligible_runs" in str(exc)
    else:
        raise AssertionError("Expected TrainingPipelineError for invalid report.")


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
        "champion": {
            "run_id": "run-tree",
            "candidate_name": "decision_tree_baseline",
            "model_type": "decision_tree",
        },
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
