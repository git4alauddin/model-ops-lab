from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMPOSE_PATH = PROJECT_ROOT / "deployment" / "docker-compose.yaml"


def _load_compose() -> dict:
    return yaml.safe_load(COMPOSE_PATH.read_text())


def test_v8_docker_compose_file_exists() -> None:
    assert COMPOSE_PATH.is_file()


def test_v8_docker_compose_defines_serving_service() -> None:
    compose = _load_compose()

    assert "services" in compose
    assert "modelopslab-serving" in compose["services"]


def test_v8_docker_compose_builds_from_serving_dockerfile() -> None:
    service = _load_compose()["services"]["modelopslab-serving"]

    assert service["build"]["context"] == ".."
    assert service["build"]["dockerfile"] == "deployment/Dockerfile"
    assert service["image"] == "modelopslab-serving:v8-c2"


def test_v8_docker_compose_exposes_serving_port() -> None:
    service = _load_compose()["services"]["modelopslab-serving"]

    assert "8000:8000" in service["ports"]


def test_v8_docker_compose_mounts_serving_runtime_state() -> None:
    service = _load_compose()["services"]["modelopslab-serving"]
    volumes = set(service["volumes"])

    assert "../model_registry:/app/model_registry:ro" in volumes
    assert "../mlruns:/app/mlruns:ro" in volumes
    assert "../logs:/app/logs" in volumes


def test_v8_docker_compose_keeps_startup_in_dockerfile() -> None:
    service = _load_compose()["services"]["modelopslab-serving"]

    assert "command" not in service
    assert service["restart"] == "unless-stopped"
