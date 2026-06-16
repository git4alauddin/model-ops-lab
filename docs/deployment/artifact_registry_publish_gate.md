# Artifact Registry Publish Gate

This guide documents the manually gated Artifact Registry publish path for ModelOpsLab.

Current scope:

```text
manual GitHub Actions trigger
Docker image build
optional Artifact Registry image publish
Git SHA image tag
no Cloud Run deployment from Artifact Registry yet
```

## Why This Gate Exists

Artifact Registry setup has already been validated:

```text
Artifact Registry API enabled
Docker repository modelopslab exists in us-central1
GitHub deploy service account has repository-level Artifact Registry Writer
```

This chunk connects the validated repository to CI publishing without changing the live deployment path yet.

Current path after this chunk:

```text
workflow_dispatch
-> tests
-> Docker image build
-> optional Artifact Registry auth and push
```

Cloud Run still deploys from Docker Hub in this chunk.

## Workflow Inputs

Run the workflow manually from:

```text
GitHub repository
-> Actions
-> ci
-> Run workflow
```

Use these inputs for Artifact Registry publishing:

```text
publish_artifact_registry: true
gcp_project_id: key-component-498805-h0
artifact_registry_location: us-central1
artifact_registry_repository: modelopslab
```

Keep these disabled if you only want to validate Artifact Registry publishing:

```text
publish_image: false
deploy_cloud_run: false
```

Reason:

```text
Docker Hub publishing and Cloud Run deployment are still separate gates
Artifact Registry publishing should be validated before Cloud Run deploys from it
```

## Required GitHub Secrets

Artifact Registry publishing uses the existing GCP secrets:

```text
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_SERVICE_ACCOUNT
```

It does not require:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

Those Docker Hub secrets are still required only for the Docker Hub publish and current Cloud Run deploy path.

## Authentication Strategy

The workflow uses:

```text
google-github-actions/auth@v3
google-github-actions/setup-gcloud@v3
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
```

Why:

```text
auth@v3 creates short-lived Google credentials through Workload Identity Federation
setup-gcloud@v3 installs and configures the gcloud CLI in the runner
gcloud auth configure-docker lets Docker authenticate to Artifact Registry
```

No service account key JSON is used.

## Image Published

The workflow publishes the Git SHA image:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:${{ github.sha }}
```

It does not publish a moving Artifact Registry `ci` tag in this chunk.

Reason:

```text
the first Artifact Registry publish gate should prove immutable source-to-image traceability
```

## Failure Behavior

The workflow fails before publishing when:

```text
GCP_WORKLOAD_IDENTITY_PROVIDER is missing
GCP_SERVICE_ACCOUNT is missing
gcp_project_id is missing
artifact_registry_location is missing
artifact_registry_repository is missing
```

The workflow fails during publishing when:

```text
Workload Identity Federation authentication fails
gcloud cannot configure Docker for the Artifact Registry host
the service account lacks roles/artifactregistry.writer on the repository
the target repository does not exist
Docker push is rejected
```

## GUI Checkpoints After A Run

In GitHub Actions:

```text
docker image build job succeeds
Authenticate to Google Cloud for Artifact Registry step succeeds
Configure Docker for Artifact Registry step succeeds
Push Artifact Registry image step succeeds
```

In Google Cloud Console:

```text
Artifact Registry
-> Repositories
-> modelopslab
-> modelopslab-serving
-> image tag matching the Git SHA
```

## Current Boundary

This gate does:

```text
build the serving image
authenticate to GCP with Workload Identity Federation
configure Docker for Artifact Registry
push the Git SHA image to Artifact Registry
```

This gate does not:

```text
deploy Cloud Run from Artifact Registry
remove Docker Hub publishing
remove Docker Hub based Cloud Run deployment
validate live /health from an Artifact Registry deployed revision
```

Those are later chunks.

## Live Validation

The first live Artifact Registry publish validation is recorded here:

```text
docs/deployment/artifact_registry_publish_validation.md
```

## Source References

- Google GitHub Action for auth: https://github.com/google-github-actions/auth
- Google GitHub Action for setup-gcloud: https://github.com/google-github-actions/setup-gcloud
- Artifact Registry Docker authentication: https://cloud.google.com/artifact-registry/docs/docker/authentication
