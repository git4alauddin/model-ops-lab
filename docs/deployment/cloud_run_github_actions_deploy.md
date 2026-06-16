# Cloud Run GitHub Actions Deployment

This guide documents the first automated Cloud Run deployment gate for ModelOpsLab.

Current scope:

```text
manual GitHub Actions trigger
Docker Hub image publish
Cloud Run deploy from exact Git SHA image
post-deploy /health validation
```

This is not a push-triggered production deployment.

## Why This Gate Exists

V8 already validates:

```text
tests
Docker build
Docker Hub publishing
Cloud Run manual console deployment path
```

This chunk connects those pieces into one controlled release path:

```text
workflow_dispatch
-> tests
-> Docker image build
-> Docker Hub publish
-> GCP authentication
-> Cloud Run deploy
-> /health check
```

The deployment remains opt-in so routine validation does not publish or deploy by accident.

## Workflow Inputs

Run the GitHub Actions workflow manually from:

```text
GitHub repository
-> Actions
-> ci
-> Run workflow
```

Use:

```text
publish_image: true
deploy_cloud_run: true
gcp_project_id: <your-gcp-project-id>
cloud_run_service: modelopslab-serving
cloud_run_region: us-central1
```

Important rule:

```text
deploy_cloud_run=true requires publish_image=true
```

Cloud Run deploys the exact Docker Hub image tagged with:

```text
${{ github.sha }}
```

It does not deploy the moving `ci` tag.

## Required GitHub Secrets

Docker Hub publishing requires:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

Cloud Run deployment requires:

```text
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_SERVICE_ACCOUNT
```

`GCP_WORKLOAD_IDENTITY_PROVIDER` must be the full Workload Identity Provider resource name.

Example shape:

```text
projects/<project-number>/locations/global/workloadIdentityPools/<pool>/providers/<provider>
```

`GCP_SERVICE_ACCOUNT` must be a service account email with enough permission to deploy Cloud Run services.

Example shape:

```text
modelopslab-deployer@<project-id>.iam.gserviceaccount.com
```

## Authentication Strategy

The workflow uses:

```text
google-github-actions/auth@v3
```

with Workload Identity Federation.

Reason:

```text
avoid storing long-lived GCP service account key JSON in GitHub
use short-lived OIDC-based authentication from GitHub Actions
keep deployment credentials scoped and revocable
```

The generated auth credentials file is ignored by both Git and Docker through:

```text
gha-creds-*.json
```

## Cloud Run Deployment Behavior

The workflow uses:

```text
google-github-actions/deploy-cloudrun@v3
```

Deployment image:

```text
docker.io/<dockerhub-username>/modelopslab-serving:<git-sha>
```

Runtime configuration:

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

Cloud Run flags:

```text
--allow-unauthenticated --port=8000
```

The first automated gate allows unauthenticated access because the workflow performs a plain HTTPS `/health` check from GitHub Actions.

Operational boundary:

```text
this is acceptable for first demo validation
private authenticated Cloud Run health checks require a later authenticated check path
```

## Post-Deploy Validation

After deployment, the workflow checks:

```text
<cloud-run-service-url>/health
```

Expected response content:

```text
status: ok
service: modelopslab-serving
```

If the service URL is missing, the health request fails, or the health payload is not valid, the deployment job fails.

## Failure Behavior

The workflow fails before deployment when:

```text
deploy_cloud_run=true and publish_image=false
DOCKERHUB_USERNAME is missing
GCP_WORKLOAD_IDENTITY_PROVIDER is missing
GCP_SERVICE_ACCOUNT is missing
gcp_project_id is missing
cloud_run_service is missing
cloud_run_region is missing
```

The workflow fails during deployment when:

```text
the Docker Hub image is unavailable
GCP authentication is invalid
the service account lacks Cloud Run deploy permissions
the Cloud Run API is disabled
Cloud Run rejects the revision
```

The workflow fails after deployment when:

```text
Cloud Run does not return a service URL
/health is unreachable
/health does not return the expected service payload
```

## Rollback Boundary

Current rollback support remains image-level:

```text
select a previous known-good Git SHA image tag
deploy that image as a new Cloud Run revision
validate /health
```

Automated Cloud Run revision rollback is not part of this chunk.

That should be handled after the first live deployment has been validated.

## Source References

- Google GitHub Action for auth: https://github.com/google-github-actions/auth
- Google GitHub Action for Cloud Run deploy: https://github.com/google-github-actions/deploy-cloudrun

## Live Validation

The first live deployment validation is recorded here:

```text
docs/deployment/cloud_run_live_validation.md
```

The Workload Identity Federation learning notes are recorded here:

```text
docs/learning/workload_identity_federation_notes.md
```

The manual CI trigger component notes are recorded here:

```text
docs/learning/manual_ci_cloud_run_trigger_notes.md
```

The Artifact Registry migration foundation is recorded here:

```text
docs/deployment/artifact_registry_foundation.md
```
