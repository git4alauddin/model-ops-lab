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
