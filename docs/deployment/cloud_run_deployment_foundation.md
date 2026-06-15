# Cloud Run Deployment Foundation

This guide prepares the first Google Cloud Run deployment path for ModelOpsLab.

V8 scope:

```text
document Cloud Run deployment foundation
guide the Google Cloud Console flow
keep GitHub Actions deployment automation for later
```

## Why Cloud Run
Cloud Run is the right first GCP deployment target for this project because:

```text
it runs containers directly
it fits the FastAPI serving API
it provides a managed HTTPS service URL
it avoids Kubernetes operational complexity
it can scale without managing servers
```

Cloud Run is a live runtime target.

Docker Hub is only an image registry.

## Image Source Choice
Current working image source:

```text
Docker Hub
```

Current published image format:

```text
<dockerhub-username>/modelopslab-serving:<git-sha>
```

Recommended production GCP direction later:

```text
Artifact Registry
```

Why Artifact Registry later:

```text
native Google Cloud registry
stronger GCP IAM integration
better fit for Cloud Run production deployments
recommended by Google over Docker Hub for GCP-native image storage
```

Why Docker Hub first:

```text
already configured
already validated
good for first Cloud Run exposure
keeps this chunk focused on deployment understanding
```

## Required GCP Setup
Before deploying:

```text
Google Cloud project exists
billing is enabled
Cloud Run API is enabled
Docker Hub image exists
image repository is public or otherwise accessible
```

Suggested service values:

```text
Service name:
modelopslab-serving

Region:
us-central1

Container port:
8000
```

## Cloud Run GUI Deployment Flow
Open Google Cloud Console:

```text
https://console.cloud.google.com/
```

Go to:

```text
Cloud Run
-> Create service
-> Deploy one revision from an existing container image
```

Use image:

```text
<dockerhub-username>/modelopslab-serving:<git-sha>
```

Configure:

```text
Service name: modelopslab-serving
Region: us-central1
Container port: 8000
```

Access choice:

```text
Allow unauthenticated invocations:
  useful for first learning/demo deployment

Require authentication:
  safer default for private production services
```

For first manual learning deployment, use unauthenticated only if you are comfortable exposing the API URL publicly.

## Environment Variables
Cloud Run should receive the same serving configuration contract used by Docker Compose.

Recommended values:

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

Important boundary:

```text
local model registry and MLflow runtime files are not automatically available in Cloud Run
```

For a real production Cloud Run deployment, model artifacts and registry metadata need a cloud-accessible storage strategy.

V8 deployment foundation focuses on container deployment mechanics first.

## Health Check
After deployment, Cloud Run provides a service URL.

Check:

```text
<cloud-run-service-url>/health
```

Expected response:

```text
status is ok
service is modelopslab-serving
```

Readiness may depend on whether model registry and MLflow artifact state are available inside the deployed container.

## Deployment Automation Boundary
Initial deployment foundation flow:

```text
Docker Hub image
-> Google Cloud Console
-> Cloud Run service
-> manual /health check
```

GitHub Actions deployment automation now lives in:

```text
docs/deployment/cloud_run_github_actions_deploy.md
```

The automated path adds:

```text
google-github-actions/auth
google-github-actions/deploy-cloudrun
deploy_cloud_run workflow input
Cloud Run service URL output
post-deploy /health check
```

Still not automated:

```text
Cloud Run revision rollback
Artifact Registry publishing
authenticated private-service health checks
```

Authentication direction:

```text
Workload Identity Federation
```

Reason:

```text
avoids long-lived service account key JSON secrets
uses short-lived GitHub OIDC-based authentication
fits production CI/CD better
```

## Source References
- Cloud Run deploy container images: https://docs.cloud.google.com/run/docs/deploying
- GitHub Action for Cloud Run deploy: https://github.com/google-github-actions/deploy-cloudrun
- GitHub Action for Google Cloud auth: https://github.com/google-github-actions/auth
