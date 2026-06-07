# V8 Overview

## Version Goal
Add Dockerization, CI/CD, and deployment automation foundations.

V8 moves the project from local serving to reproducible release engineering.

## Completion Status
V8 is in progress.

Implemented chunks:
- V8-C1: Docker serving image foundation.

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
