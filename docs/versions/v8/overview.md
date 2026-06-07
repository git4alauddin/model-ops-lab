# V8 Overview

## Version Goal
Add Dockerization, CI/CD, and deployment automation foundations.

V8 moves the project from local serving to reproducible release engineering.

## Completion Status
V8 is in progress.

Implemented chunks:
- V8-C1: Docker serving image foundation.
- V8-C2: Docker Compose serving runtime.
- V8-C3: serving environment configuration.
- V8-C4: CI test workflow.
- V8-C5: CI Docker image build gate.
- V8-C6: Docker image versioning contract.
- V8-C7: manual CI run guide.

## Components To Introduce
- Docker serving image
- Docker build context control
- Docker Compose local runtime
- environment-based configuration
- CI test gate
- CI image build gate
- image versioning
- deployment validation
- rollback documentation
- deployment flow diagram

## V8 Direction
V8 starts with containerizing the serving API boundary.

This is the correct first step because V7 already exposes:

```text
app.serve_api:app
```

The first V8 container should prove the API can run from a clean image with installed dependencies before adding Compose, CI/CD, registry push, or deployment automation.

V8-C2 adds Docker Compose so the same serving image can be started with a repeatable local runtime definition.

V8-C3 makes serving runtime behavior explicit through environment variables so Docker, Compose, and future CI/CD runs use the same configuration contract.

V8-C4 adds the first automated CI quality gate through GitHub Actions.

V8-C5 adds a Docker image build gate after tests pass.

V8-C6 adds explicit image tagging rules before Docker Hub publishing.

The CI workflow uses manual execution during the current build phase to avoid spending CI minutes on every small push.

V8-C7 documents how to trigger and read that manual workflow.

## Docker Boundary
The V8-C1 image packages source code and Python dependencies.

It intentionally excludes local runtime state:

```text
artifacts/
logs/
mlruns/
model_registry/
pipeline_runs/
reports/
mlflow.db
```

Those are environment/runtime concerns. They should be mounted, generated, or provided later through controlled deployment configuration instead of being baked into the image.

## Initial Container Command

```powershell
docker build -f deployment/Dockerfile -t modelopslab-serving:v8-c1 .
docker run --rm -p 8000:8000 modelopslab-serving:v8-c1
```

## Docker Compose Runtime

```powershell
docker compose -f deployment/docker-compose.yaml up --build
```

Compose provides:

```text
serving container build
localhost:8000 port mapping
read-only model_registry mount
read-only mlruns mount
writable logs mount
```

## Serving Environment Configuration
Serving runtime settings are documented in `.env.example`.

Current keys:

```text
MODELOPSLAB_ENV
SERVING_HOST
SERVING_PORT
LOG_LEVEL
MODEL_REGISTRY_DIR
MLFLOW_RUNS_DIR
PREDICTION_LOG_PATH
APP_LOG_PATH
```

These settings control container startup, model registry lookup, MLflow artifact lookup, prediction audit logs, and master app logs.

Expected initial behavior:

```text
GET /health works
GET /ready depends on mounted or provided champion model runtime state
```

## Operational Objectives
- make the serving runtime reproducible
- isolate Python dependencies from the host machine
- keep secrets and runtime artifacts outside the image
- prepare for Docker Compose
- prepare for CI image builds
- prepare for deployment validation

## CI Foundation
The CI workflow is triggered manually:

```text
workflow_dispatch
```

The workflow installs dependencies from `requirements.txt` and runs:

```powershell
python -m pytest -q
```

Manual trigger is intentional during the learning/build phase to avoid spending CI minutes on every small push.

Run from GitHub UI:

```text
GitHub repo
-> Actions
-> ci
-> Run workflow
-> select main
-> Run workflow
```

## CI Docker Build Gate
The CI workflow now has two jobs:

```text
tests
docker-image
```

The Docker image job depends on the test job:

```text
tests pass
-> build serving Docker image
```

This validates that the deployment image can be built in CI before any registry push or deployment automation exists.

## Docker Image Versioning
Docker image tagging is documented here:

```text
deployment/image_tags.md
```

CI builds use:

```text
modelopslab-serving:ci
modelopslab-serving:${{ github.sha }}
```

The `ci` tag is a temporary validation tag. The Git SHA tag is traceable to an exact commit and prepares the project for rollback-safe registry publishing.

## Manual CI Run Guide
Manual CI operation is documented here:

```text
docs/deployment/ci_manual_run_guide.md
```

The guide explains when to run CI, how to trigger it from GitHub Actions, what each job means, and how to inspect failures.
