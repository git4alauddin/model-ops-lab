"""Environment-based settings for the serving runtime."""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Mapping


DEFAULT_MODELOPSLAB_ENV = "local"
DEFAULT_SERVING_HOST = "0.0.0.0"
DEFAULT_SERVING_PORT = 8000
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_MODEL_REGISTRY_DIR = Path("model_registry")
DEFAULT_MLFLOW_RUNS_DIR = Path("mlruns")
DEFAULT_PREDICTION_LOG_PATH = Path("logs/predictions.jsonl")
DEFAULT_APP_LOG_PATH = Path("logs/modelopslab.log")
DEFAULT_DEPLOYMENT_VERSION = "local"


class ServingSettingsError(ValueError):
    """Raised when serving environment configuration is invalid."""


@dataclass(frozen=True)
class ServingSettings:
    """Resolved serving runtime configuration."""

    modelopslab_env: str = DEFAULT_MODELOPSLAB_ENV
    serving_host: str = DEFAULT_SERVING_HOST
    serving_port: int = DEFAULT_SERVING_PORT
    log_level: str = DEFAULT_LOG_LEVEL
    model_registry_dir: Path = DEFAULT_MODEL_REGISTRY_DIR
    mlflow_runs_dir: Path = DEFAULT_MLFLOW_RUNS_DIR
    prediction_log_path: Path = DEFAULT_PREDICTION_LOG_PATH
    app_log_path: Path = DEFAULT_APP_LOG_PATH
    deployment_version: str = DEFAULT_DEPLOYMENT_VERSION


def get_serving_settings(
    environ: Mapping[str, str] | None = None,
) -> ServingSettings:
    """Resolve serving settings from environment variables."""
    env = os.environ if environ is None else environ
    return ServingSettings(
        modelopslab_env=_read_string(env, "MODELOPSLAB_ENV", DEFAULT_MODELOPSLAB_ENV),
        serving_host=_read_string(env, "SERVING_HOST", DEFAULT_SERVING_HOST),
        serving_port=_read_port(env, "SERVING_PORT", DEFAULT_SERVING_PORT),
        log_level=_read_string(env, "LOG_LEVEL", DEFAULT_LOG_LEVEL).upper(),
        model_registry_dir=_read_path(
            env,
            "MODEL_REGISTRY_DIR",
            DEFAULT_MODEL_REGISTRY_DIR,
        ),
        mlflow_runs_dir=_read_path(env, "MLFLOW_RUNS_DIR", DEFAULT_MLFLOW_RUNS_DIR),
        prediction_log_path=_read_path(
            env,
            "PREDICTION_LOG_PATH",
            DEFAULT_PREDICTION_LOG_PATH,
        ),
        app_log_path=_read_path(env, "APP_LOG_PATH", DEFAULT_APP_LOG_PATH),
        deployment_version=_read_string(
            env,
            "DEPLOYMENT_VERSION",
            DEFAULT_DEPLOYMENT_VERSION,
        ),
    )


def _read_string(
    environ: Mapping[str, str],
    key: str,
    default: str,
) -> str:
    value = environ.get(key, default).strip()
    if not value:
        raise ServingSettingsError(f"{key} must not be empty.")
    return value


def _read_port(
    environ: Mapping[str, str],
    key: str,
    default: int,
) -> int:
    value = environ.get(key)
    if value is None or value.strip() == "":
        return default
    try:
        port = int(value)
    except ValueError as exc:
        raise ServingSettingsError(f"{key} must be an integer.") from exc
    if not 1 <= port <= 65535:
        raise ServingSettingsError(f"{key} must be between 1 and 65535.")
    return port


def _read_path(
    environ: Mapping[str, str],
    key: str,
    default: Path,
) -> Path:
    value = environ.get(key)
    if value is None or value.strip() == "":
        return default
    return Path(value)
