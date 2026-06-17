from pathlib import Path

import pytest
import yaml

from app.serving.settings import (
    ServingSettingsError,
    get_serving_settings,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMPOSE_PATH = PROJECT_ROOT / "deployment" / "docker-compose.yaml"
ENV_EXAMPLE_PATH = PROJECT_ROOT / ".env.example"


def test_serving_settings_use_local_safe_defaults() -> None:
    settings = get_serving_settings({})

    assert settings.modelopslab_env == "local"
    assert settings.serving_host == "0.0.0.0"
    assert settings.serving_port == 8000
    assert settings.log_level == "INFO"
    assert settings.model_registry_dir == Path("model_registry")
    assert settings.mlflow_runs_dir == Path("mlruns")
    assert settings.prediction_log_path == Path("logs/predictions.jsonl")
    assert settings.app_log_path == Path("logs/modelopslab.log")
    assert settings.deployment_version == "local"


def test_serving_settings_accept_environment_overrides() -> None:
    settings = get_serving_settings(
        {
            "MODELOPSLAB_ENV": "staging",
            "SERVING_HOST": "127.0.0.1",
            "SERVING_PORT": "9000",
            "LOG_LEVEL": "debug",
            "MODEL_REGISTRY_DIR": "/runtime/registry",
            "MLFLOW_RUNS_DIR": "/runtime/mlruns",
            "PREDICTION_LOG_PATH": "/runtime/logs/predictions.jsonl",
            "APP_LOG_PATH": "/runtime/logs/modelopslab.log",
            "DEPLOYMENT_VERSION": "revision-1",
        }
    )

    assert settings.modelopslab_env == "staging"
    assert settings.serving_host == "127.0.0.1"
    assert settings.serving_port == 9000
    assert settings.log_level == "DEBUG"
    assert settings.model_registry_dir == Path("/runtime/registry")
    assert settings.mlflow_runs_dir == Path("/runtime/mlruns")
    assert settings.prediction_log_path == Path("/runtime/logs/predictions.jsonl")
    assert settings.app_log_path == Path("/runtime/logs/modelopslab.log")
    assert settings.deployment_version == "revision-1"


def test_serving_settings_reject_invalid_port() -> None:
    with pytest.raises(ServingSettingsError, match="SERVING_PORT"):
        get_serving_settings({"SERVING_PORT": "not-a-port"})

    with pytest.raises(ServingSettingsError, match="SERVING_PORT"):
        get_serving_settings({"SERVING_PORT": "70000"})


def test_env_example_documents_serving_runtime_keys() -> None:
    env_example = ENV_EXAMPLE_PATH.read_text()

    expected_keys = [
        "MODELOPSLAB_ENV=",
        "SERVING_HOST=",
        "SERVING_PORT=",
        "LOG_LEVEL=",
        "DEPLOYMENT_VERSION=",
        "MODEL_REGISTRY_DIR=",
        "MLFLOW_RUNS_DIR=",
        "PREDICTION_LOG_PATH=",
        "APP_LOG_PATH=",
    ]

    for key in expected_keys:
        assert key in env_example


def test_docker_compose_passes_serving_environment() -> None:
    service = yaml.safe_load(COMPOSE_PATH.read_text())["services"]["modelopslab-serving"]
    environment = service["environment"]

    assert service["env_file"] == ["../.env.example"]
    assert environment["MODELOPSLAB_ENV"] == "${MODELOPSLAB_ENV:-local}"
    assert environment["SERVING_HOST"] == "${SERVING_HOST:-0.0.0.0}"
    assert environment["SERVING_PORT"] == "${SERVING_PORT:-8000}"
    assert environment["LOG_LEVEL"] == "${LOG_LEVEL:-info}"
    assert environment["DEPLOYMENT_VERSION"] == "${DEPLOYMENT_VERSION:-local}"
    assert environment["MODEL_REGISTRY_DIR"] == "/app/model_registry"
    assert environment["MLFLOW_RUNS_DIR"] == "/app/mlruns"
    assert environment["PREDICTION_LOG_PATH"] == "/app/logs/predictions.jsonl"
    assert environment["APP_LOG_PATH"] == "/app/logs/modelopslab.log"


def test_dockerfile_uses_serving_environment_for_uvicorn_startup() -> None:
    dockerfile = (PROJECT_ROOT / "deployment" / "Dockerfile").read_text()

    assert "${SERVING_HOST:-0.0.0.0}" in dockerfile
    assert "${SERVING_PORT:-8000}" in dockerfile
    assert "${LOG_LEVEL:-info}" in dockerfile
