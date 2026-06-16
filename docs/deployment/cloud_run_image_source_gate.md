# Cloud Run Image Source Gate

This guide documents the Cloud Run deployment image source selector for ModelOpsLab.

Current scope:

```text
manual GitHub Actions trigger
Docker Hub image source remains the default
Artifact Registry image source is available
post-deploy /health validation remains unchanged
```

This chunk changes the deployment gate shape, but it does not validate a live Artifact Registry Cloud Run deployment yet.

## Why This Gate Exists

The project now has two validated image publishing paths:

```text
Docker Hub
Artifact Registry
```

Cloud Run needs to know which image source to deploy from.

The workflow uses an explicit input:

```text
cloud_run_image_source: dockerhub | artifact_registry
```

This is clearer than a boolean because the value names the image source directly.

## Inputs

Default Docker Hub deployment path:

```text
publish_image: true
publish_artifact_registry: false
deploy_cloud_run: true
cloud_run_image_source: dockerhub
gcp_project_id: key-component-498805-h0
cloud_run_service: modelopslab-serving
cloud_run_region: us-central1
```

Artifact Registry deployment path:

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

## Image Resolution

When `cloud_run_image_source=dockerhub`, Cloud Run deploys:

```text
docker.io/${DOCKERHUB_USERNAME}/modelopslab-serving:${{ github.sha }}
```

Required:

```text
publish_image=true
DOCKERHUB_USERNAME
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_SERVICE_ACCOUNT
```

When `cloud_run_image_source=artifact_registry`, Cloud Run deploys:

```text
${artifact_registry_location}-docker.pkg.dev/${gcp_project_id}/${artifact_registry_repository}/modelopslab-serving:${{ github.sha }}
```

For the current project, that resolves to:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:${{ github.sha }}
```

Required:

```text
publish_artifact_registry=true
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_SERVICE_ACCOUNT
gcp_project_id
artifact_registry_location
artifact_registry_repository
```

## Validation Rules

The workflow fails before deploying when:

```text
cloud_run_image_source is not dockerhub or artifact_registry
dockerhub source is selected but publish_image is not true
artifact_registry source is selected but publish_artifact_registry is not true
required GCP secrets are missing
required project, service, or region inputs are missing
required Artifact Registry inputs are missing for artifact_registry source
```

The workflow resolves the image in a dedicated step:

```text
Resolve Cloud Run image
```

The deploy action then uses:

```text
steps.cloud-run-image.outputs.image
```

## Current Boundary

This gate does:

```text
keep Docker Hub as the default Cloud Run image source
allow Artifact Registry as an explicit Cloud Run image source
preserve Git SHA image deployment
preserve post-deploy /health validation
```

This gate does not:

```text
trigger a live Artifact Registry Cloud Run deployment
validate /health from an Artifact Registry deployed revision
remove Docker Hub deployment support
remove Docker Hub secrets
```

Those are later chunks.

## Next Chunk Direction

The next deployment chunk should validate this input set live:

```text
publish_image=false
publish_artifact_registry=true
deploy_cloud_run=true
cloud_run_image_source=artifact_registry
gcp_project_id=key-component-498805-h0
cloud_run_service=modelopslab-serving
cloud_run_region=us-central1
artifact_registry_location=us-central1
artifact_registry_repository=modelopslab
```

Expected result:

```text
GitHub Actions
-> pytest
-> Docker image build
-> Artifact Registry image push
-> Cloud Run deploy from Artifact Registry image
-> /health check
```
