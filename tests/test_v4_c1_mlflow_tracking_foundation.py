"""Tests for V4 MLflow tracking foundation."""

from contextlib import contextmanager

from app.experiment_tracking import (
    build_experiment_tracking_config,
    build_mlflow_params,
    ExperimentTrackingError,
    get_run_id,
    log_training_outputs,
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

    assert params["pipeline_version"] == "v4-c1"
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
        }
    }
    artifact_paths = {
        "metrics": tmp_path / "metrics.json",
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
    assert fake_mlflow.logged_metrics == {"accuracy": 1.0}
    assert fake_mlflow.logged_artifacts == [
        str(artifact_paths["metrics"]),
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
