"""MLflow experiment tracking helpers for V4."""

from contextlib import contextmanager
from importlib import import_module
from pathlib import Path
import sys
from typing import Any, Iterator


class ExperimentTrackingError(ValueError):
    """Raised when experiment tracking setup or logging fails."""


DEFAULT_EXPERIMENT_NAME = "modelopslab"
DEFAULT_TRACKING_URI = "sqlite:///mlflow.db"
PIPELINE_VERSION = "v4-c2"


def build_experiment_tracking_config(config: dict[str, Any]) -> dict[str, str]:
    """Return MLflow tracking settings from config with safe defaults."""
    tracking_config = config.get("experiment_tracking")
    if not isinstance(tracking_config, dict):
        return {
            "experiment_name": DEFAULT_EXPERIMENT_NAME,
            "tracking_uri": DEFAULT_TRACKING_URI,
        }

    experiment_name = tracking_config.get("experiment_name") or DEFAULT_EXPERIMENT_NAME
    tracking_uri = tracking_config.get("tracking_uri") or DEFAULT_TRACKING_URI
    if not isinstance(experiment_name, str):
        raise ExperimentTrackingError("experiment_tracking.experiment_name must be a string.")
    if not isinstance(tracking_uri, str):
        raise ExperimentTrackingError("experiment_tracking.tracking_uri must be a string.")

    return {
        "experiment_name": experiment_name,
        "tracking_uri": tracking_uri,
    }


def build_mlflow_params(
    config: dict[str, Any],
    training_metadata: dict[str, Any],
) -> dict[str, str | int | float | bool]:
    """Build flat MLflow params from training config and metadata."""
    training_config = config["training"]
    model_config = config["model"]
    dataset_version = training_metadata["dataset_version"]
    checksum = dataset_version.get("checksum") or {}

    return {
        "pipeline_version": PIPELINE_VERSION,
        "model_type": str(model_config["type"]),
        "test_size": float(training_config["test_size"]),
        "random_state": int(training_config["random_state"]),
        "dataset_name": str(dataset_version["dataset_name"]),
        "dataset_version": str(dataset_version["version"]),
        "dataset_path": str(dataset_version["path"]),
        "dataset_checksum_algorithm": str(checksum.get("algorithm")),
        "dataset_checksum": str(checksum.get("value")),
    }


@contextmanager
def start_experiment_run(
    config: dict[str, Any],
    run_name: str,
    mlflow_module: Any | None = None,
) -> Iterator[Any]:
    """Configure MLflow and start a run context."""
    mlflow = mlflow_module or _load_mlflow()
    tracking_config = build_experiment_tracking_config(config)

    try:
        mlflow.set_tracking_uri(tracking_config["tracking_uri"])
        mlflow.set_experiment(tracking_config["experiment_name"])
    except Exception as exc:
        raise ExperimentTrackingError("Failed to configure MLflow tracking.") from exc

    run_context = mlflow.start_run(run_name=run_name)
    try:
        run = run_context.__enter__()
    except Exception as exc:
        raise ExperimentTrackingError("Failed to start MLflow run.") from exc

    exc_info = (None, None, None)
    try:
        yield run
    except Exception as exc:
        exc_info = sys.exc_info()
        try:
            _log_failed_run_tags(mlflow, exc)
        except Exception:
            pass
        raise
    finally:
        run_context.__exit__(*exc_info)


def get_run_id(run: Any) -> str:
    """Extract an MLflow run ID from an active run object."""
    try:
        return str(run.info.run_id)
    except AttributeError as exc:
        raise ExperimentTrackingError("MLflow run does not expose run_id.") from exc


def log_training_outputs(
    config: dict[str, Any],
    metrics: dict[str, Any],
    training_metadata: dict[str, Any],
    artifact_paths: dict[str, Path],
    mlflow_module: Any | None = None,
) -> None:
    """Log training params, metrics, and artifacts to the active MLflow run."""
    mlflow = mlflow_module or _load_mlflow()
    params = build_mlflow_params(config, training_metadata)
    metric_values = build_mlflow_metrics(metrics, training_metadata)

    try:
        mlflow.log_params(params)
        mlflow.log_metrics(metric_values)
        for artifact_path in artifact_paths.values():
            mlflow.log_artifact(str(artifact_path))
    except Exception as exc:
        raise ExperimentTrackingError("Failed to log MLflow training outputs.") from exc


def build_mlflow_metrics(
    metrics: dict[str, Any],
    training_metadata: dict[str, Any],
) -> dict[str, float]:
    """Build flat MLflow metrics from evaluation metrics and training metadata."""
    metric_values = _filter_numeric_metrics(metrics)
    metric_values["training_duration_seconds"] = float(
        training_metadata["training_duration_seconds"]
    )
    metric_values["evaluation_duration_seconds"] = float(
        training_metadata["evaluation_duration_seconds"]
    )
    return metric_values


def log_failed_run(
    error: Exception,
    mlflow_module: Any | None = None,
) -> None:
    """Log failure details to the active MLflow run."""
    mlflow = mlflow_module or _load_mlflow()
    try:
        _log_failed_run_tags(mlflow, error)
    except Exception as exc:
        raise ExperimentTrackingError("Failed to log MLflow failure details.") from exc


def _log_failed_run_tags(mlflow: Any, error: Exception) -> None:
    mlflow.set_tag("run_outcome", "failed")
    mlflow.set_tag("failure_type", error.__class__.__name__)
    mlflow.set_tag("failure_message", str(error))


def _filter_numeric_metrics(metrics: dict[str, Any]) -> dict[str, float]:
    return {
        key: float(value)
        for key, value in metrics.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    }


def _load_mlflow() -> Any:
    try:
        return import_module("mlflow")
    except ImportError as exc:
        raise ExperimentTrackingError("MLflow is not installed.") from exc
