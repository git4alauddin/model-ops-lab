# V8 Verification

## Checks Performed
- Verified Dockerfile exists.
- Verified Dockerfile uses a Python slim runtime image.
- Verified Dockerfile installs project requirements.
- Verified Dockerfile starts `app.serve_api:app` through Uvicorn.
- Verified Dockerfile exposes port `8000`.
- Verified `.dockerignore` exists.
- Verified `.dockerignore` excludes local runtime state, secrets, virtual environment, and caches.
- Verified source code, configs, and requirements remain available to the Docker build context.
- Verified Docker Compose file exists.
- Verified Docker Compose defines the serving service.
- Verified Docker Compose builds from `deployment/Dockerfile`.
- Verified Docker Compose exposes port `8000`.
- Verified Docker Compose mounts local serving runtime state.
- Verified Docker Compose leaves app startup owned by the Dockerfile.

## Commands Executed
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py`
- `python -m pytest -q`
- `docker --version`
- `docker build -f deployment/Dockerfile -t modelopslab-serving:v8-c1 .`
- `docker run --rm modelopslab-serving:v8-c1 python -c "from app.serve_api import app; print(app.title); print(app.version)"`
- `python -m pytest -q tests\test_v8_c2_docker_compose_runtime.py`
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py`
- `docker compose -f deployment/docker-compose.yaml config`
- `docker compose -f deployment/docker-compose.yaml build`
- `docker compose -f deployment/docker-compose.yaml run --rm modelopslab-serving python -c "from app.serve_api import app; print(app.title); print(app.version)"`
- `docker compose -f deployment/docker-compose.yaml up -d --build`
- `Invoke-RestMethod http://127.0.0.1:8000/health`
- `docker compose -f deployment/docker-compose.yaml down`
- `python -m pytest -q`
- `git diff --check`

## Expected Output
- Docker serving foundation tests pass.
- Existing test suite remains passing.
- Docker is available locally.
- Docker image builds successfully when Docker Desktop is running.
- Docker build context excludes local runtime-heavy folders.
- Dockerfile can start the FastAPI serving API inside the image.
- Built image can import the FastAPI serving app.
- Docker Compose config is valid.
- Docker Compose can build the serving image.
- Docker Compose can run the service image and import the FastAPI app.
- Docker Compose can start the serving container and expose `/health`.

## Actual Output
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py` passed: `5 passed in 0.05s`.
- `python -m pytest -q` passed: `304 passed in 7.00s`.
- `docker --version` printed `Docker version 29.2.1, build a5c7197`.
- `docker build -f deployment/Dockerfile -t modelopslab-serving:v8-c1 .` built successfully.
- `docker run --rm modelopslab-serving:v8-c1 python -c "from app.serve_api import app; print(app.title); print(app.version)"` printed `ModelOpsLab Serving API` and `v7`.
- `python -m pytest -q tests\test_v8_c2_docker_compose_runtime.py` passed: `6 passed in 0.07s`.
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py` passed: `11 passed in 0.09s`.
- `docker compose -f deployment/docker-compose.yaml config` resolved the service, build context, port mapping, and runtime mounts successfully.
- `docker compose -f deployment/docker-compose.yaml build` built `modelopslab-serving:v8-c2` successfully.
- `docker compose -f deployment/docker-compose.yaml run --rm modelopslab-serving python -c "from app.serve_api import app; print(app.title); print(app.version)"` printed `ModelOpsLab Serving API` and `v7`.
- Compose runtime `/health` check returned `{"status":"ok","service":"modelopslab-serving","api_version":"v7"}`.
- `python -m pytest -q` passed: `310 passed in 20.96s`.
- `git diff --check` passed with CRLF normalization warnings only.

## Outcome
V8-C1 adds the first reproducible serving image boundary.

The API can now be packaged separately from the local Python virtual environment. Runtime model state remains outside the image by design.

V8-C2 adds a repeatable Docker Compose runtime for local serving with controlled mounts for model registry metadata, MLflow artifacts, and logs.
