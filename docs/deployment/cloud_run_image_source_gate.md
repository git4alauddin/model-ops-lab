# Cloud Run Image Source Gate

This guide documents the Cloud Run deployment image source selector for ModelOpsLab.

Current scope:

```text
manual GitHub Actions trigger
Artifact Registry image source is the default
Docker Hub image source remains available as a fallback
post-deploy /health validation remains unchanged
```

Artifact Registry is the preferred image source after the live Cloud Run deployment validation.

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

Default Artifact Registry deployment path:

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

Docker Hub fallback deployment path:

```text
publish_image: true
publish_artifact_registry: false
deploy_cloud_run: true
cloud_run_image_source: dockerhub
gcp_project_id: key-component-498805-h0
cloud_run_service: modelopslab-serving
cloud_run_region: us-central1
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
keep Artifact Registry as the default Cloud Run image source
keep Docker Hub as an explicit fallback Cloud Run image source
preserve Git SHA image deployment
preserve post-deploy /health validation
```

This gate does not:

```text
remove Docker Hub deployment support
remove Docker Hub secrets
```

Those are later chunks.

## Default Source

The default Artifact Registry deploy source is documented here:

```text
docs/deployment/artifact_registry_default_deploy_source.md
```

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

## Live Validation

The first live Cloud Run deployment from Artifact Registry is recorded here:

```text
docs/deployment/cloud_run_artifact_registry_deploy_validation.md
```
