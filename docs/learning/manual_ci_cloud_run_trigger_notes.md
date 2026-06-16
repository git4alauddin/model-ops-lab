# Manual CI Cloud Run Trigger Notes

These notes explain the components involved when the GitHub Actions workflow is triggered manually for a Cloud Run deployment.

This is the learning guide for what we saw in the GitHub UI during the first live deployment validation.

## Big Picture

The manual trigger starts from GitHub Actions:

```text
GitHub repository
-> Actions
-> ci
-> Run workflow
```

The deployment path is:

```text
workflow_dispatch
-> pytest job
-> Docker image job
-> Docker Hub push
-> Cloud Run deploy job
-> Workload Identity Federation auth
-> Cloud Run revision update
-> /health validation
```

The important idea:

```text
the workflow is one button in the UI, but several systems participate behind it
```

## Trigger Type

The workflow uses:

```text
workflow_dispatch
```

That means:

```text
the workflow can be started manually from the GitHub Actions UI
the user can provide input values before the workflow starts
the deployment remains opt-in
normal pushes do not deploy unless the workflow logic says so
```

In this project, the manual trigger is used because deployment should not happen automatically while the deployment foundation is still being learned and validated.

## Inputs We Set

The manual run used these inputs:

```text
publish_image: true
deploy_cloud_run: true
gcp_project_id: key-component-498805-h0
cloud_run_service: modelopslab-serving
cloud_run_region: us-central1
```

### publish_image

Purpose:

```text
controls whether the Docker image is pushed to Docker Hub
```

When `publish_image=true`:

```text
GitHub Actions logs in to Docker Hub
the serving image is built
the image is tagged with the exact Git SHA
the image is pushed to Docker Hub
```

Why this matters:

```text
Cloud Run needs an image it can pull
the deploy job should not point to an image that was never published
```

### deploy_cloud_run

Purpose:

```text
controls whether the Cloud Run deployment job runs
```

When `deploy_cloud_run=true`:

```text
GitHub Actions authenticates to Google Cloud
the workflow deploys the exact Git SHA image to Cloud Run
the workflow checks the deployed /health endpoint
```

Important rule:

```text
deploy_cloud_run=true requires publish_image=true
```

Reason:

```text
Cloud Run deploy uses the image produced by the workflow
if the image was not published, Cloud Run has nothing new to deploy
```

### gcp_project_id

Purpose:

```text
tells the deploy action which Google Cloud project receives the Cloud Run service update
```

Current project:

```text
key-component-498805-h0
```

### cloud_run_service

Purpose:

```text
names the Cloud Run service to create or update
```

Current service:

```text
modelopslab-serving
```

### cloud_run_region

Purpose:

```text
tells Cloud Run which regional control plane to use
```

Current region:

```text
us-central1
```

The service URL includes regional routing after deployment.

## Jobs In The Workflow

### pytest job

Purpose:

```text
prove the repository tests pass before building or deploying
```

If this job fails:

```text
the image job should not publish a new image
the Cloud Run deploy job should not run
```

This happened during the live validation when the serving closure test used route metadata assumptions that differed in CI.

### Docker image job

Purpose:

```text
build the serving Docker image
optionally publish it to Docker Hub
```

The important image tag is:

```text
${{ github.sha }}
```

Why:

```text
the deployment points to an immutable commit-specific image tag
we can trace the Cloud Run revision back to the exact source commit
```

The moving `ci` tag is useful for build validation, but it is not the deployment identity.

### Cloud Run deploy job

Purpose:

```text
authenticate to GCP
deploy the Git SHA image to Cloud Run
validate /health after deployment
```

This job depends on the Docker image job because Cloud Run must pull an image that already exists.

## GitHub Secrets

The manual run does not type secret values into the workflow form.

Instead, GitHub Actions reads secrets configured under:

```text
GitHub repository
-> Settings
-> Secrets and variables
-> Actions
```

Secrets used:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_SERVICE_ACCOUNT
```

What each one does:

```text
DOCKERHUB_USERNAME: Docker Hub account used for image push
DOCKERHUB_TOKEN: Docker Hub token used for registry login
GCP_WORKLOAD_IDENTITY_PROVIDER: full Google provider resource trusted by GitHub Actions
GCP_SERVICE_ACCOUNT: service account email GitHub Actions impersonates
```

Secret values are never recorded in the docs.

## Google Cloud Components

### Workload Identity Pool

Purpose:

```text
container for external identities Google Cloud can trust
```

Current pool:

```text
github-actions-pool
```

### Workload Identity Provider

Purpose:

```text
defines GitHub Actions as the external identity source
maps GitHub OIDC token claims into Google attributes
```

Current provider:

```text
github-actions-provider
```

### Service Account

Purpose:

```text
the GCP identity used by the deployment job
```

Current service account:

```text
modelopslab-github-deployer@key-component-498805-h0.iam.gserviceaccount.com
```

Roles used:

```text
roles/run.admin
roles/iam.serviceAccountUser
```

### Workload Identity User Binding

Purpose:

```text
allows the specific GitHub repository identity to impersonate the service account
```

Repository restriction:

```text
git4alauddin/model-ops-lab
```

This is the trust link between GitHub and the service account.

## Docker Hub Component

Docker Hub stores the published serving image:

```text
alaudddin/modelopslab-serving:<git-sha>
```

Cloud Run pulls this image during deployment.

During the live validation, Docker Hub already had the public image tag, but the first Cloud Run deploy attempt failed through `mirror.gcr.io` because the fresh public image was not immediately available through the pull path. Rerunning the failed deploy job succeeded.

Learning:

```text
public Docker Hub visibility and Cloud Run pull availability may not become true at exactly the same second
```

## Cloud Run Component

Cloud Run receives the image and creates a revision.

The live validation created the ready revision:

```text
modelopslab-serving-00002-fbc
```

The service URL was:

```text
https://modelopslab-serving-pv3rkohw6q-uc.a.run.app
```

The workflow then checked:

```text
GET /health
```

Expected response:

```text
{"status":"ok","service":"modelopslab-serving","api_version":"v7"}
```

## What To Watch In The GUI

In GitHub Actions:

```text
workflow run status
pytest job
docker image job
cloud run deploy job
rerun failed jobs option
logs for image tag, service URL, and health response
```

In Docker Hub:

```text
repository visibility
image tag
last pushed time
digest
```

In Google Cloud Console:

```text
Cloud Run service
latest revision
traffic split
service URL
logs
IAM service account
Workload Identity pool and provider
```

## Failure Points To Remember

Common failures:

```text
tests fail before image build
Docker Hub credentials are missing or wrong
publish_image is false while deploy_cloud_run is true
GCP Workload Identity provider secret is wrong
service account secret is wrong
service account lacks Cloud Run permissions
repository binding does not match the GitHub repository
Cloud Run API is disabled
fresh Docker Hub image is not immediately pullable
/health does not return the expected payload
```

The useful debugging order:

```text
check which job failed
read the first failing step inside that job
confirm whether the image tag exists
confirm whether GitHub authenticated to GCP
confirm whether Cloud Run created a new revision
confirm whether /health responded
```

## Mental Model

Think of the manual deployment as this chain:

```text
GitHub button
-> workflow inputs
-> repository secrets
-> test gate
-> image build and push
-> short-lived GCP auth
-> Cloud Run revision
-> health check
```

Each stage has a different responsibility. When deployment fails, the first task is to identify which stage broke.
