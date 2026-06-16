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
- V8-C8: Docker Hub publishing plan.
- V8-C9: Docker Hub secrets setup guide.
- V8-C10: manual Docker Hub publish gate.
- V8-C11: Docker Hub publish validation.
- V8-C12: Docker rollback guide.
- V8-C13: Cloud Run deployment foundation.

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

V8-C8 documents Docker Hub publishing requirements before credentials or push steps are added.

V8-C9 documents Docker Hub token and GitHub Actions secrets setup before CI login or push steps are added.

V8-C10 adds a manually controlled Docker Hub publish gate while keeping publishing disabled by default.

V8-C11 records that the Docker Hub repository, GitHub Actions secrets, and manual publish workflow were configured and validated.

V8-C12 documents rollback behavior for Docker images using exact Git SHA image tags.

V8-C13 documents the manual Google Cloud Run deployment foundation and keeps CI-based GCP deployment automation for later.

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

## Docker Hub Publishing Plan
Docker Hub publishing is planned here:

```text
docs/deployment/dockerhub_publishing_plan.md
```

The plan defines required GitHub secrets, target image naming, token usage, planned push tags, and the current no-push boundary.

## Docker Hub Secrets Setup
Docker Hub credential setup is documented here:

```text
docs/deployment/dockerhub_secrets_setup.md
```

The guide explains how to create a Docker Hub access token and add these GitHub Actions repository secrets:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

Current CI still does not login to Docker Hub or push images.

## Manual Docker Hub Publish Gate
Docker Hub publishing is now available from the manual CI workflow only when explicitly enabled.

Default manual run:

```text
publish_image: false
```

Publish run:

```text
publish_image: true
```

Publish operation is documented here:

```text
docs/deployment/dockerhub_publish_run_guide.md
```

The workflow still runs tests before image build and publish.

## Docker Hub Publish Validation
Docker Hub publishing has been validated here:

```text
docs/deployment/dockerhub_publish_validation.md
```

Validated boundary:

```text
tests
-> Docker image build
-> Docker Hub secret validation
-> Docker Hub login
-> Docker Hub push
-> Docker Hub tags visible
```

V8 still does not deploy to a live cloud runtime.

## Docker Rollback
Docker image rollback is documented here:

```text
docs/deployment/docker_rollback_guide.md
```

Rollback rule:

```text
use <git-sha>
do not use ci
```

The `ci` tag is a moving tag. Git SHA tags are stable rollback targets.

Cloud Run rollback is intentionally left for the later live deployment chunk.

## Cloud Run Deployment Foundation
Cloud Run deployment foundation is documented here:

```text
docs/deployment/cloud_run_deployment_foundation.md
```

Current target:

```text
Docker Hub image
-> manual Cloud Run deployment
-> /health check
```

Current boundary:

```text
Cloud Run GUI walkthrough exists
GitHub Actions manual deployment gate exists
Artifact Registry migration remains later scope
```

## Cloud Run GitHub Actions Deployment
Cloud Run deployment automation is documented here:

```text
docs/deployment/cloud_run_github_actions_deploy.md
```

Deployment flow:

```text
workflow_dispatch
-> tests
-> Docker image build
-> Docker Hub publish
-> Workload Identity Federation auth
-> Cloud Run deploy
-> /health check
```

Current boundary:

```text
deploy_cloud_run defaults to false
publish_image must be true before deployment
the Git SHA image tag is deployed
post-deploy /health is checked from GitHub Actions
Cloud Run revision rollback remains later scope
Artifact Registry remains later scope
```

## Live Cloud Run Deployment Validation
Live deployment validation is recorded here:

```text
docs/deployment/cloud_run_live_validation.md
```

Validated flow:

```text
GitHub Actions
-> pytest
-> Docker image build
-> Docker Hub push
-> Workload Identity Federation auth
-> Cloud Run deploy
-> /health check
```

Learning notes for Workload Identity Federation are recorded here:

```text
docs/learning/workload_identity_federation_notes.md
```

Learning notes for the manual CI trigger components are recorded here:

```text
docs/learning/manual_ci_cloud_run_trigger_notes.md
```

## Artifact Registry Foundation
Artifact Registry migration foundation is documented here:

```text
docs/deployment/artifact_registry_foundation.md
```

Target image path:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:<git-sha>
```

Current boundary:

```text
Artifact Registry setup guide exists
GitHub Actions still publishes to Docker Hub
Artifact Registry publishing remains later scope
live Artifact Registry deployment remains later scope
```

## Artifact Registry Setup Validation
Artifact Registry setup validation is recorded here:

```text
docs/deployment/artifact_registry_setup_validation.md
```

Validated setup:

```text
Artifact Registry API enabled
Docker repository modelopslab exists in us-central1
registry URI is us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab
GitHub deploy service account has roles/artifactregistry.writer on the repository
```

Current boundary:

```text
no image has been pushed to Artifact Registry yet
GitHub Actions still publishes to Docker Hub
Cloud Run still deploys from Docker Hub
Artifact Registry publishing remains later scope
```
