# Cloud Run Live Validation

This records the first live Cloud Run deployment validation for ModelOpsLab.

## Validation Status

```text
status: successful after retry
date: 2026-06-16
workflow run: 27637437455
workflow URL: https://github.com/git4alauddin/model-ops-lab/actions/runs/27637437455
```

## Deployment Target

```text
GCP project ID: key-component-498805-h0
GCP project number: 153930851596
Cloud Run service: modelopslab-serving
Region: us-central1
Runtime access: unauthenticated for first demo health validation
```

## GitHub Actions Inputs

```text
publish_image: true
deploy_cloud_run: true
gcp_project_id: key-component-498805-h0
cloud_run_service: modelopslab-serving
cloud_run_region: us-central1
```

## GitHub Actions Secrets Used

Secret names:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_SERVICE_ACCOUNT
```

No secret values were recorded.

## Image Deployed

```text
Docker Hub repository: alaudddin/modelopslab-serving
Git SHA tag: 4388088e4b5f605a552ecf4e46d4edaab2a8e7fb
Digest: sha256:62ff4b9ac2487e3457972958cc4f0531bd9700ae639b265dff903a7c0127f71b
```

Cloud Run deploy command used by GitHub Actions:

```text
gcloud run deploy modelopslab-serving
  --image docker.io/<dockerhub-username>/modelopslab-serving:4388088e4b5f605a552ecf4e46d4edaab2a8e7fb
  --region us-central1
  --project key-component-498805-h0
  --allow-unauthenticated
  --port 8000
```

## Successful Deployment Evidence

Successful GitHub Actions jobs:

```text
pytest: success
docker image build: success
cloud run deploy: success after failed-job rerun
```

GitHub Actions test result:

```text
387 passed, 2 warnings in 5.38s
```

Cloud Run service URL:

```text
https://modelopslab-serving-pv3rkohw6q-uc.a.run.app
```

Cloud Run revision:

```text
latest ready revision: modelopslab-serving-00002-fbc
traffic: 100
```

GitHub Actions health check:

```json
{"status":"ok","service":"modelopslab-serving","api_version":"v7"}
```

Local external health check:

```json
{"status":"ok","service":"modelopslab-serving","api_version":"v7"}
```

## Failure During Validation

The first Cloud Run deploy attempt failed after successful GCP authentication.

Failure:

```text
ERROR: (gcloud.run.deploy) Image 'mirror.gcr.io/alaudddin/modelopslab-serving:4388088e4b5f605a552ecf4e46d4edaab2a8e7fb' not found.
```

What had already succeeded before the failure:

```text
Docker Hub login
Docker image push
Docker Hub tag creation
GCP Workload Identity authentication
Cloud Run service creation attempt
```

Verification showed the Docker Hub repository was public and the exact tag existed:

```text
repository: alaudddin/modelopslab-serving
is_private: False
tag: 4388088e4b5f605a552ecf4e46d4edaab2a8e7fb
digest: sha256:62ff4b9ac2487e3457972958cc4f0531bd9700ae639b265dff903a7c0127f71b
```

Resolution:

```text
reran the failed cloud run deploy job after the Docker Hub tag was visible externally
```

The rerun succeeded.

## Operational Interpretation

This was not an IAM failure.

Evidence:

```text
GCP authentication succeeded
Workload Identity Federation created a temporary credential file
Cloud Run deploy command executed
Cloud Run service was created
```

The failure was image availability between Docker Hub and Cloud Run's pull path for a newly pushed public tag.

Operational lesson:

```text
Docker Hub is acceptable for first demo deployment, but Artifact Registry is the stronger production direction for GCP-native Cloud Run deployments.
```

## Remaining Boundaries

Not included in this validation:

```text
Artifact Registry publishing
private authenticated Cloud Run access
Cloud Run rollback automation
production traffic strategy
model artifact externalization
readiness endpoint validation with cloud-hosted model registry artifacts
```

Only `/health` was validated because the current Cloud Run image does not include local model registry and MLflow runtime files.
