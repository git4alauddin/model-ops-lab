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

## V8-C5: CI Docker Image Build Gate

### Files Added

```text
tests/test_v8_c5_ci_docker_build.py
```

### Files Updated

```text
.github/workflows/ci.yaml
docs/versions/v8/
```

### Behavior
- Added a `docker-image` job to the CI workflow.
- Made the Docker image job depend on the `tests` job.
- Checked out the repository before building the image.
- Built the serving image with `deployment/Dockerfile`.
- Tagged the CI-built image as `modelopslab-serving:ci`.
- Did not add Docker Hub login.
- Did not push the image to any registry.
- Added static workflow tests for the Docker build gate.

### CI Flow

```text
push or pull request
-> tests job
-> docker-image job
-> docker build -f deployment/Dockerfile -t modelopslab-serving:ci .
```

### Boundary
V8-C5 only verifies that the image can build in CI.

Docker Hub authentication, image push, semantic image tags, and deployment automation remain separate later chunks.

## V8-C6: Docker Image Versioning Contract

### Files Added

```text
deployment/image_tags.md
tests/test_v8_c6_image_versioning.py
```

### Files Updated

```text
.github/workflows/ci.yaml
tests/test_v8_c5_ci_docker_build.py
docs/versions/v8/
```

### Behavior
- Added a Docker image tagging contract.
- Documented CI, Git SHA, semantic release, and optional `latest` tags.
- Warned against using `latest` as the only deployed or rollback tag.
- Updated CI Docker build to tag images as `modelopslab-serving:ci`.
- Updated CI Docker build to also tag images as `modelopslab-serving:${{ github.sha }}`.
- Kept Docker Hub login and image push out of the workflow.
- Added focused tests for image versioning and no-push behavior.

### CI Build Command

```text
docker build \
  -f deployment/Dockerfile \
  -t modelopslab-serving:ci \
  -t modelopslab-serving:${{ github.sha }} \
  .
```

### Boundary
V8-C6 defines traceable image tags.

Docker Hub authentication, Docker Hub push, release tagging, and deployment automation remain separate later chunks.

## V8-C7: Manual CI Run Guide

### Files Added

```text
docs/deployment/ci_manual_run_guide.md
tests/test_v8_c7_ci_manual_run_guide.py
```

### Files Updated

```text
README.md
docs/versions/v8/
```

### Behavior
- Added manual CI run guide.
- Documented when to run CI manually.
- Documented GitHub Actions UI trigger path.
- Explained the `tests` job.
- Explained the `docker-image` job.
- Explained how to inspect pytest failures.
- Explained how to inspect Docker build failures.
- Documented that Docker Hub login, image push, and cloud deployment are not implemented yet.
- Added tests for the guide.

### Manual Run Flow

```text
GitHub repo
-> Actions
-> ci
-> Run workflow
-> select main
-> Run workflow
```

### Boundary
V8-C7 documents CI operation.

It does not add Docker Hub push, deployment automation, or production secrets.

## V8-C8: Docker Hub Publishing Plan

### Files Added

```text
docs/deployment/dockerhub_publishing_plan.md
tests/test_v8_c8_dockerhub_publishing_plan.py
```

### Files Updated

```text
README.md
docs/versions/v8/
```

### Behavior
- Added Docker Hub publishing plan.
- Explained Docker Hub as the external image registry.
- Defined target image naming format.
- Documented required GitHub Actions secrets.
- Documented why Docker Hub token should be used instead of password.
- Documented planned Git SHA and CI push tags.
- Documented GitHub UI path for adding repository secrets.
- Documented that Docker Hub push is not enabled yet.
- Added tests that verify the plan and confirm CI still does not publish images.

### Required Secrets Later

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

### Boundary
V8-C8 plans Docker Hub publishing.

It does not add Docker login, Docker push, registry credentials, or deployment automation.

## V8-C9: Docker Hub Secrets Setup Guide

### Files Added

```text
docs/deployment/dockerhub_secrets_setup.md
tests/test_v8_c9_dockerhub_secrets_setup.py
```

### Files Updated

```text
README.md
docs/versions/v8/
```

### Behavior
- Added a Docker Hub secrets setup guide.
- Documented Docker Hub access token creation from the Docker Hub UI.
- Documented GitHub Actions repository secret creation from the GitHub UI.
- Documented required secret names: `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`.
- Documented token usage instead of account password.
- Documented safe verification without exposing secret values.
- Documented that tokens must not be printed, committed, or pasted into `.env` files.
- Added tests that verify the guide and confirm CI still does not login or push.

### Boundary
V8-C9 prepares credential setup.

It does not add Docker login, Docker push, or image publishing to CI.

## V8-C10: Manual Docker Hub Publish Gate

### Files Added

```text
docs/deployment/dockerhub_publish_run_guide.md
tests/test_v8_c10_dockerhub_publish_gate.py
```

### Files Updated

```text
.github/workflows/ci.yaml
README.md
docs/deployment/README.md
docs/versions/v8/
tests/test_v8_c5_ci_docker_build.py
tests/test_v8_c6_image_versioning.py
tests/test_v8_c8_dockerhub_publishing_plan.py
tests/test_v8_c9_dockerhub_secrets_setup.py
```

### Behavior
- Kept CI manual-only through `workflow_dispatch`.
- Added manual `publish_image` input with default value `false`.
- Kept Docker image build running after tests.
- Added Docker Hub login only when `publish_image` is `true`.
- Added Docker Hub tag steps only when `publish_image` is `true`.
- Added Docker Hub push steps only when `publish_image` is `true`.
- Pushes the Git SHA tag and `ci` tag.
- Added a Docker Hub publish run guide for GitHub Actions UI operation.
- Updated earlier no-push tests to assert the new guarded-publish contract.

### Boundary
V8-C10 adds manual Docker Hub publishing.

It does not add automatic publish on push, production deployment, release tags, or cloud hosting.

## V8-C11: Docker Hub Publish Validation

### Files Added

```text
docs/deployment/dockerhub_publish_validation.md
tests/test_v8_c11_dockerhub_publish_validation.py
```

### Files Updated

```text
docs/deployment/README.md
docs/deployment/dockerhub_publish_run_guide.md
docs/versions/v8/
```

### Behavior
- Recorded completed Docker Hub repository configuration.
- Recorded completed GitHub Actions secret configuration.
- Recorded successful manual publish workflow behavior.
- Documented expected Docker Hub image tags.
- Clarified that V8 validates Docker Hub publishing but does not deploy to Cloud Run or another live cloud runtime.

### Boundary
V8-C11 closes the Docker Hub publishing validation loop.

Cloud Run deployment remains a later deployment chunk.

## V8-C12: Docker Rollback Guide

### Files Added

```text
docs/deployment/docker_rollback_guide.md
tests/test_v8_c12_docker_rollback_guide.py
```

### Files Updated

```text
docs/deployment/README.md
docs/versions/v8/
```

### Behavior
- Added Docker rollback guide.
- Documented rollback with exact Git SHA image tags.
- Warned against using the moving `ci` tag as a rollback target.
- Documented how to find previous known-good image tags in Docker Hub.
- Documented local `docker pull` and `docker run` rollback checks.
- Clarified that Cloud Run rollback is outside the current V8 scope.

### Boundary
V8-C12 documents image-level rollback readiness.

Live service rollback will be handled when Cloud Run deployment exists.
