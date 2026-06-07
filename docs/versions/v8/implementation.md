# V8 Implementation

## V8-C1: Docker Serving Image Foundation

### Files Added

```text
deployment/Dockerfile
.dockerignore
tests/test_v8_c1_docker_serving_foundation.py
docs/versions/v8/
```

### Files Updated

```text
README.md
```

### Behavior
- Added a Dockerfile for the FastAPI serving app.
- Used `python:3.11-slim` as the runtime base image.
- Installed dependencies from `requirements.txt`.
- Copied project source into `/app`.
- Exposed port `8000`.
- Started serving with `uvicorn app.serve_api:app`.
- Added `.dockerignore` to keep local runtime state, virtual environments, caches, and secrets out of the image build context.
- Added focused static tests for Dockerfile and `.dockerignore` behavior.

### Image Build

```powershell
docker build -f deployment/Dockerfile -t modelopslab-serving:v8-c1 .
```

### Local Container Run

```powershell
docker run --rm -p 8000:8000 modelopslab-serving:v8-c1
```

### Important Boundary
The image does not bake in local runtime model state.

Excluded from image context:

```text
artifacts/
logs/
mlruns/
model_registry/
pipeline_runs/
reports/
mlflow.db
```

This keeps the image reusable. Model artifacts and registry state should be supplied later through Docker Compose volumes, object storage, or deployment environment configuration.

## V8-C2: Docker Compose Serving Runtime

### Files Added

```text
deployment/docker-compose.yaml
tests/test_v8_c2_docker_compose_runtime.py
```

### Files Updated

```text
README.md
docs/versions/v8/
```

### Behavior
- Added a Docker Compose runtime for the serving API.
- Built the service from `deployment/Dockerfile`.
- Tagged the Compose-built image as `modelopslab-serving:v8-c2`.
- Mapped host port `8000` to container port `8000`.
- Mounted local `model_registry/` into the container read-only.
- Mounted local `mlruns/` into the container read-only.
- Mounted local `logs/` into the container as writable runtime output.
- Kept the startup command in the Dockerfile instead of duplicating it in Compose.

### Compose Run

```powershell
docker compose -f deployment/docker-compose.yaml up --build
```

### Compose Health Check

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### Runtime Mount Boundary
Compose supplies the local runtime state that the image intentionally excludes.

```text
../model_registry -> /app/model_registry:ro
../mlruns         -> /app/mlruns:ro
../logs           -> /app/logs
```

## V8-C3: Serving Environment Configuration

### Files Added

```text
app/serving/settings.py
tests/test_v8_c3_serving_environment_config.py
```

### Files Updated

```text
.env.example
deployment/Dockerfile
deployment/docker-compose.yaml
app/api/routes.py
tests/test_v7_c2_readiness_endpoint.py
tests/test_v7_c6_predict_endpoint.py
tests/test_v7_c7_prediction_logging.py
tests/test_v7_c8_batch_prediction_endpoint.py
tests/test_v7_c9_serving_runtime_logging.py
tests/test_v8_c1_docker_serving_foundation.py
tests/test_v8_c2_docker_compose_runtime.py
docs/versions/v8/
```

### Behavior
- Added typed serving runtime settings.
- Added local-safe defaults for host, port, log level, registry path, MLflow path, prediction log path, and app log path.
- Added validation for serving port values.
- Documented serving environment variables in `.env.example`.
- Updated Docker startup to read `SERVING_HOST`, `SERVING_PORT`, and `LOG_LEVEL`.
- Updated Docker Compose to pass explicit serving environment variables.
- Updated API routes to use configured registry, MLflow, prediction log, and app log paths.
- Kept model registry and MLflow mounts read-only while keeping logs writable.

### Environment Keys

```text
MODELOPSLAB_ENV=local
SERVING_HOST=0.0.0.0
SERVING_PORT=8000
LOG_LEVEL=info
MODEL_REGISTRY_DIR=model_registry
MLFLOW_RUNS_DIR=mlruns
PREDICTION_LOG_PATH=logs/predictions.jsonl
APP_LOG_PATH=logs/modelopslab.log
```

### Compose Config Check

```powershell
docker compose -f deployment/docker-compose.yaml --env-file .env.example config
```

### Compose Runtime Check

```powershell
docker compose -f deployment/docker-compose.yaml --env-file .env.example up -d --build
Invoke-RestMethod http://127.0.0.1:8000/health
docker compose -f deployment/docker-compose.yaml --env-file .env.example down
```

### Issue Found During Verification
Uvicorn rejects uppercase log levels such as `INFO`.

The deployment-facing default uses lowercase `info`, while Python settings normalize `LOG_LEVEL` to uppercase internally.

## V8-C4: CI Test Workflow

### Files Added

```text
.github/workflows/ci.yaml
tests/test_v8_c4_ci_workflow.py
```

### Files Updated

```text
docs/versions/v8/
```

### Behavior
- Added GitHub Actions CI workflow.
- Runs on pushes to `main`.
- Runs on pull requests targeting `main`.
- Checks out the repository.
- Sets up Python `3.11`.
- Enables pip dependency caching from `requirements.txt`.
- Installs dependencies from `requirements.txt`.
- Runs the full test suite with `python -m pytest -q`.
- Added static workflow tests to verify the CI contract.

### CI Flow

```text
git push
-> GitHub Actions starts ci workflow
-> checkout repository
-> setup Python
-> install requirements
-> run pytest
```

### Boundary
V8-C4 only adds the test gate.

Docker image build gates, registry push, and deployment validation are intentionally left for later V8 chunks.
