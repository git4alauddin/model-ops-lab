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
