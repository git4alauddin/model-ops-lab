# Cloud Run Artifact Registry Deployment Validation

This records the first live Cloud Run deployment from an Artifact Registry image for ModelOpsLab.

## Validation Status

```text
status: successful
date: 2026-06-17
workflow run: 27645315977
workflow URL: https://github.com/git4alauddin/model-ops-lab/actions/runs/27645315977
trigger: workflow_dispatch
```

GitHub run timestamps were recorded in UTC:

```text
createdAt: 2026-06-16T20:16:13Z
updatedAt: 2026-06-16T20:21:26Z
```

## Workflow Inputs

```text
publish_image: false
publish_artifact_registry: true
deploy_cloud_run: true
cloud_run_image_source: artifact_registry
gcp_project_id: key-component-498805-h0
cloud_run_service: modelopslab-serving
cloud_run_region: us-central1
artifact_registry_location: us-central1
artifact_registry_repository: modelopslab
```

Why this input set was used:

```text
publish a fresh Git SHA image to Artifact Registry
deploy Cloud Run from Artifact Registry
keep Docker Hub publishing disabled
validate the deployed /health endpoint
```

## Source Commit

```text
commit: ee825dad109380d7f53e4a576de0fd2b042e704a
short commit: ee825da
message: v8-c21: add Cloud Run image source gate
```

## GitHub Actions Result

Workflow result:

```text
status: completed
conclusion: success
```

Jobs:

```text
pytest: success
docker image build: success
cloud run deploy: success
```

Job IDs:

```text
pytest: 81755575750
docker image build: 81755802258
cloud run deploy: 81756154931
```

Docker Hub steps were skipped:

```text
Validate Docker Hub secrets: skipped
Login to Docker Hub: skipped
Tag Docker Hub image: skipped
Push Docker Hub image: skipped
```

Artifact Registry publish steps succeeded:

```text
Validate Artifact Registry inputs: success
Authenticate to Google Cloud for Artifact Registry: success
Set up Google Cloud SDK: success
Configure Docker for Artifact Registry: success
Tag Artifact Registry image: success
Push Artifact Registry image: success
```

Cloud Run deploy steps succeeded:

```text
Validate Cloud Run deployment inputs: success
Resolve Cloud Run image: success
Authenticate to Google Cloud: success
Deploy to Cloud Run: success
Validate deployed health endpoint: success
Report Cloud Run URL: success
```

## Artifact Registry Image Evidence

Package:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving
```

Published tag:

```text
ee825dad109380d7f53e4a576de0fd2b042e704a
```

Full tag reference:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:ee825dad109380d7f53e4a576de0fd2b042e704a
```

Digest:

```text
sha256:ae9949f46c754d650936175fb6c58e6413bc32716a541f1426400160159fb50b
```

Artifact Registry metadata:

```text
createTime: 2026-06-16T20:19:15.506815Z
updateTime: 2026-06-16T20:19:15.506815Z
buildTime: 2026-06-16T20:18:20.687086249Z
imageSizeBytes: 332661375
mediaType: application/vnd.docker.distribution.manifest.v2+json
```

Command used:

```powershell
gcloud artifacts docker images list us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab --include-tags --format=json
```

## Cloud Run Deployment Evidence

Service:

```text
name: modelopslab-serving
project: key-component-498805-h0
region: us-central1
service URL: https://modelopslab-serving-pv3rkohw6q-uc.a.run.app
```

Latest ready revision:

```text
modelopslab-serving-00003-zsc
```

Traffic:

```text
revision: modelopslab-serving-00003-zsc
percent: 100
```

Cloud Run service image tag:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:ee825dad109380d7f53e4a576de0fd2b042e704a
```

Cloud Run revision image digest:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving@sha256:ae9949f46c754d650936175fb6c58e6413bc32716a541f1426400160159fb50b
```

Revision labels:

```text
commit-sha: ee825dad109380d7f53e4a576de0fd2b042e704a
managed-by: github-actions
```

Runtime environment remained unchanged:

```text
MODELOPSLAB_ENV=cloud-run
SERVING_HOST=0.0.0.0
SERVING_PORT=8000
LOG_LEVEL=info
MODEL_REGISTRY_DIR=model_registry
MLFLOW_RUNS_DIR=mlruns
PREDICTION_LOG_PATH=logs/predictions.jsonl
APP_LOG_PATH=logs/modelopslab.log
```

Command used:

```powershell
gcloud run services describe modelopslab-serving --region=us-central1 --project=key-component-498805-h0 --format=json
gcloud run revisions describe modelopslab-serving-00003-zsc --region=us-central1 --project=key-component-498805-h0 --format=json
```

## Health Validation

External health check:

```powershell
Invoke-RestMethod -Uri 'https://modelopslab-serving-pv3rkohw6q-uc.a.run.app/health'
```

Response:

```json
{"status":"ok","service":"modelopslab-serving","api_version":"v7"}
```

The GitHub Actions post-deploy health step also succeeded.

## Boundary Confirmed

Validated:

```text
Artifact Registry publishing works
cloud_run_image_source=artifact_registry resolves the Artifact Registry image
Cloud Run deploys the Artifact Registry image
Cloud Run revision records the Artifact Registry digest
post-deploy /health succeeds
100% traffic routes to the new revision
```

Still not done:

```text
remove Docker Hub deployment support
remove Docker Hub secrets
validate /ready or prediction endpoints in Cloud Run
externalize model registry and MLflow artifacts for full prediction readiness
add rollback automation for Cloud Run revisions
```

Rollback and cleanup guidance is recorded here:

```text
docs/deployment/cloud_run_rollback_cleanup_guide.md
```

## Outcome

Artifact Registry is now a validated end-to-end image source for Cloud Run:

```text
GitHub Actions
-> pytest
-> Docker image build
-> Artifact Registry push
-> Cloud Run deploy from Artifact Registry
-> /health check
```
