# V8 Commit Log

## Pending - v8-c1: add Docker serving image foundation

### What Changed
- Added Dockerfile for the FastAPI serving API.
- Added Docker build context exclusions with `.dockerignore`.
- Added focused Docker foundation tests.
- Added V8 documentation scaffold.
- Added a minimal README Docker serving entry point.

### What Problem It Solved
- Creates the first reproducible container boundary for the serving API.
- Prevents local runtime artifacts, logs, MLflow state, model registry files, virtual environments, and secrets from being baked into the image.

### Verification
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py` passed: `5 passed in 0.05s`.
- `python -m pytest -q` passed: `304 passed in 7.00s`.
- `docker --version` printed `Docker version 29.2.1, build a5c7197`.
- `docker build -f deployment/Dockerfile -t modelopslab-serving:v8-c1 .` built successfully.
- `docker run --rm modelopslab-serving:v8-c1 python -c "from app.serve_api import app; print(app.title); print(app.version)"` printed `ModelOpsLab Serving API` and `v7`.
- `git diff --check` passed with CRLF normalization warnings only.

## Pending - v8-c2: add Docker Compose serving runtime

### What Changed
- Added Docker Compose runtime for the serving API.
- Built the service from `deployment/Dockerfile`.
- Added local port mapping for `8000:8000`.
- Mounted local `model_registry/` and `mlruns/` read-only.
- Mounted local `logs/` as writable output.
- Added focused Docker Compose runtime tests.
- Updated README and V8 docs.

### What Problem It Solved
- Replaces manual `docker run` flags with a repeatable local runtime definition.
- Defines how the containerized serving API receives local model metadata, MLflow artifacts, and log output.

### Verification
- `python -m pytest -q tests\test_v8_c2_docker_compose_runtime.py` passed: `6 passed in 0.07s`.
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py` passed: `11 passed in 0.09s`.
- `docker compose -f deployment/docker-compose.yaml config` resolved the service, build context, port mapping, and runtime mounts successfully.
- `docker compose -f deployment/docker-compose.yaml build` built `modelopslab-serving:v8-c2` successfully.
- `docker compose -f deployment/docker-compose.yaml run --rm modelopslab-serving python -c "from app.serve_api import app; print(app.title); print(app.version)"` printed `ModelOpsLab Serving API` and `v7`.
- Compose runtime `/health` check returned `{"status":"ok","service":"modelopslab-serving","api_version":"v7"}`.
- `python -m pytest -q` passed: `310 passed in 20.96s`.
- `git diff --check` passed with CRLF normalization warnings only.
