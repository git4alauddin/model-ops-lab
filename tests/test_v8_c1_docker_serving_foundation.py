from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE_PATH = PROJECT_ROOT / "deployment" / "Dockerfile"
DOCKERIGNORE_PATH = PROJECT_ROOT / ".dockerignore"


def test_v8_dockerfile_exists() -> None:
    assert DOCKERFILE_PATH.is_file()


def test_v8_dockerfile_packages_serving_api() -> None:
    dockerfile = DOCKERFILE_PATH.read_text()

    assert "FROM python:3.11-slim" in dockerfile
    assert "WORKDIR /app" in dockerfile
    assert "COPY requirements.txt ." in dockerfile
    assert "python -m pip install --no-cache-dir -r requirements.txt" in dockerfile
    assert "COPY . ." in dockerfile
    assert "EXPOSE 8000" in dockerfile
    assert "uvicorn app.serve_api:app" in dockerfile
    assert "${SERVING_HOST:-0.0.0.0}" in dockerfile
    assert "${SERVING_PORT:-8000}" in dockerfile
    assert "${LOG_LEVEL:-info}" in dockerfile


def test_v8_dockerignore_exists() -> None:
    assert DOCKERIGNORE_PATH.is_file()


def test_v8_dockerignore_excludes_local_runtime_state() -> None:
    ignored_paths = set(DOCKERIGNORE_PATH.read_text().splitlines())

    expected_ignored_paths = {
        "vir_env/",
        ".env",
        ".env.*",
        "artifacts/",
        "logs/",
        "mlruns/",
        "mlartifacts/",
        "model_registry/",
        "pipeline_runs/",
        "reports/",
        "mlflow.db*",
    }

    assert expected_ignored_paths.issubset(ignored_paths)


def test_v8_dockerignore_keeps_source_and_config_available() -> None:
    ignored_paths = set(DOCKERIGNORE_PATH.read_text().splitlines())

    assert "app/" not in ignored_paths
    assert "configs/" not in ignored_paths
    assert "requirements.txt" not in ignored_paths
