"""Tests for V4 MLflow tracking foundation."""

from contextlib import contextmanager

import pandas as pd

from app.experiment_tracking import (
    build_experiment_tracking_config,
    build_mlflow_metrics,
    build_mlflow_params,
    clear_champion_tags,
    ExperimentTrackingError,
    get_run_id,
    log_training_outputs,
    set_run_tags,
    start_experiment_run,
)


def test_build_experiment_tracking_config_from_config():
    config = {
        "experiment_tracking": {
            "experiment_name": "customer_churn_baseline",
            "tracking_uri": "sqlite:///mlflow.db",
        }
    }

    tracking_config = build_experiment_tracking_config(config)

    assert tracking_config["experiment_name"] == "customer_churn_baseline"
    assert tracking_config["tracking_uri"] == "sqlite:///mlflow.db"


def test_build_mlflow_params_includes_dataset_version_context():
    config = {
        "training": {"test_size": 0.2, "random_state": 42},
        "model": {"type": "logistic_regression"},
    }
    metadata = {
        "dataset_version": {
            "dataset_name": "customer_churn",
            "version": "v1",
            "path": "data/churn.csv",
            "checksum": {
                "algorithm": "sha256",
                "value": "abc123",
            },
        }
    }

    params = build_mlflow_params(config, metadata)

    assert params["pipeline_version"] == "v4-c6"
    assert params["model_type"] == "logistic_regression"
    assert params["test_size"] == 0.2
    assert params["random_state"] == 42
    assert params["dataset_name"] == "customer_churn"
    assert params["dataset_version"] == "v1"
    assert params["dataset_checksum_algorithm"] == "sha256"
    assert params["dataset_checksum"] == "abc123"


def test_start_experiment_run_configures_mlflow():
    fake_mlflow = FakeMlflow()
    config = {
        "experiment_tracking": {
            "experiment_name": "customer_churn_baseline",
            "tracking_uri": "sqlite:///mlflow.db",
        }
    }

    with start_experiment_run(config, "test-run", fake_mlflow) as run:
        run_id = get_run_id(run)

    assert fake_mlflow.tracking_uri == "sqlite:///mlflow.db"
    assert fake_mlflow.experiment_name == "customer_churn_baseline"
    assert fake_mlflow.started_run_name == "test-run"
    assert run_id == "run-123"


def test_log_training_outputs_logs_params_metrics_and_artifacts(tmp_path):
    fake_mlflow = FakeMlflow()
    config = {
        "training": {"test_size": 0.2, "random_state": 42},
        "model": {"type": "logistic_regression"},
    }
    metadata = {
        "dataset_version": {
            "dataset_name": "customer_churn",
            "version": "v1",
            "path": "data/churn.csv",
            "checksum": {
                "algorithm": "sha256",
                "value": "abc123",
            },
        },
        "training_duration_seconds": 0.4,
        "evaluation_duration_seconds": 0.2,
    }
    artifact_paths = {
        "metrics": tmp_path / "metrics.json",
        "confusion_matrix": tmp_path / "confusion_matrix.json",
        "metadata": tmp_path / "training_metadata.json",
    }

    log_training_outputs(
        config,
        {"accuracy": 1.0, "confusion_matrix": [[1, 0], [0, 1]]},
        metadata,
        artifact_paths,
        fake_mlflow,
    )

    assert fake_mlflow.logged_params["dataset_version"] == "v1"
    assert fake_mlflow.logged_metrics == {
        "accuracy": 1.0,
        "training_duration_seconds": 0.4,
        "evaluation_duration_seconds": 0.2,
    }
    assert fake_mlflow.logged_artifacts == [
        str(artifact_paths["metrics"]),
        str(artifact_paths["confusion_matrix"]),
        str(artifact_paths["metadata"]),
    ]


def test_invalid_experiment_tracking_config_fails_safely():
    config = {"experiment_tracking": {"experiment_name": 123}}

    try:
        build_experiment_tracking_config(config)
    except ExperimentTrackingError as exc:
        assert "experiment_name" in str(exc)
    else:
        raise AssertionError("Expected ExperimentTrackingError for invalid config.")


def test_build_mlflow_metrics_includes_training_and_evaluation_duration():
    metrics = {"accuracy": 1.0, "confusion_matrix": [[1, 0], [0, 1]]}
    metadata = {
        "training_duration_seconds": 0.5,
        "evaluation_duration_seconds": 0.25,
    }

    mlflow_metrics = build_mlflow_metrics(metrics, metadata)

    assert mlflow_metrics == {
        "accuracy": 1.0,
        "training_duration_seconds": 0.5,
        "evaluation_duration_seconds": 0.25,
    }


def test_start_experiment_run_tags_failed_run_on_body_error():
    fake_mlflow = FakeMlflow()
    config = {
        "experiment_tracking": {
            "experiment_name": "customer_churn_baseline",
            "tracking_uri": "sqlite:///mlflow.db",
        }
    }

    try:
        with start_experiment_run(config, "failing-run", fake_mlflow):
            raise RuntimeError("simulated training failure")
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected RuntimeError from failing run body.")

    assert fake_mlflow.logged_tags["run_outcome"] == "failed"
    assert fake_mlflow.logged_tags["failure_type"] == "RuntimeError"
    assert fake_mlflow.logged_tags["failure_message"] == "simulated training failure"


def test_start_experiment_run_preserves_body_error_when_failure_tagging_fails():
    fake_mlflow = FailingTagMlflow()
    config = {
        "experiment_tracking": {
            "experiment_name": "customer_churn_baseline",
            "tracking_uri": "sqlite:///mlflow.db",
        }
    }

    try:
        with start_experiment_run(config, "failing-run", fake_mlflow):
            raise RuntimeError("original training failure")
    except RuntimeError as exc:
        assert str(exc) == "original training failure"
    else:
        raise AssertionError("Expected original RuntimeError from failing run body.")


def test_set_run_tags_updates_existing_run():
    fake_mlflow = FakeMlflow()
    config = {
        "experiment_tracking": {
            "experiment_name": "customer_churn_baseline",
            "tracking_uri": "sqlite:///mlflow.db",
        }
    }

    set_run_tags(
        config,
        "run-123",
        {"champion": "true", "champion_reason": "highest_f1"},
        fake_mlflow,
    )

    assert fake_mlflow.tracking_uri == "sqlite:///mlflow.db"
    assert fake_mlflow.client.logged_tags == [
        ("run-123", "champion", "true"),
        ("run-123", "champion_reason", "highest_f1"),
    ]


def test_clear_champion_tags_marks_existing_champions_false():
    fake_mlflow = FakeMlflow()
    fake_mlflow.search_runs_result = pd.DataFrame(
        [
            {"run_id": "run-old", "tags.champion": "true"},
            {"run_id": "run-other", "tags.champion": "false"},
        ]
    )
    config = {
        "experiment_tracking": {
            "experiment_name": "customer_churn_baseline",
            "tracking_uri": "sqlite:///mlflow.db",
        }
    }

    cleared_count = clear_champion_tags(config, fake_mlflow)

    assert cleared_count == 1
    assert fake_mlflow.client.logged_tags == [("run-old", "champion", "false")]


class FakeRunInfo:
    run_id = "run-123"


class FakeRun:
    info = FakeRunInfo()


class FakeMlflow:
    def __init__(self) -> None:
        self.tracking_uri = None
        self.experiment_name = None
        self.started_run_name = None
        self.logged_params = {}
        self.logged_metrics = {}
        self.logged_artifacts = []
        self.logged_tags = {}
        self.client = FakeMlflowClient()
        self.search_runs_result = pd.DataFrame()

    def set_tracking_uri(self, tracking_uri: str) -> None:
        self.tracking_uri = tracking_uri

    def set_experiment(self, experiment_name: str) -> None:
        self.experiment_name = experiment_name

    @contextmanager
    def start_run(self, run_name: str):
        self.started_run_name = run_name
        yield FakeRun()

    def log_params(self, params: dict) -> None:
        self.logged_params = params

    def log_metrics(self, metrics: dict) -> None:
        self.logged_metrics = metrics

    def log_artifact(self, artifact_path: str) -> None:
        self.logged_artifacts.append(artifact_path)

    def set_tag(self, key: str, value: str) -> None:
        self.logged_tags[key] = value

    def MlflowClient(self):
        return self.client

    def search_runs(self, experiment_names: list[str]):
        self.searched_experiment_names = experiment_names
        return self.search_runs_result


class FailingTagMlflow(FakeMlflow):
    def set_tag(self, key: str, value: str) -> None:
        raise RuntimeError("tag write failed")


class FakeMlflowClient:
    def __init__(self) -> None:
        self.logged_tags = []

    def set_tag(self, run_id: str, key: str, value: str) -> None:
        self.logged_tags.append((run_id, key, value))
