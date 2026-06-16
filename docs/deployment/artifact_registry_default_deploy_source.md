# Artifact Registry Default Deploy Source

This guide records the deployment default after validating Cloud Run from Artifact Registry.

## Current Default

Cloud Run deployment now defaults to:

```text
cloud_run_image_source: artifact_registry
```

Default Artifact Registry image path:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:${{ github.sha }}
```

Docker Hub remains available as an explicit fallback:

```text
cloud_run_image_source: dockerhub
```

## Why The Default Changed

Artifact Registry has been validated for:

```text
repository setup
GitHub Actions image publishing
Cloud Run deployment
post-deploy /health validation
```

The validated GCP-native path is now:

```text
GitHub Actions
-> pytest
-> Docker image build
-> Artifact Registry push
-> Cloud Run deploy from Artifact Registry
-> /health check
```

This removes Docker Hub pull-through timing from the preferred Cloud Run deployment path.

## Recommended Manual Deployment Inputs

Use this for the preferred GCP-native deployment path:

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

Use this only for fallback Docker Hub deployment:

```text
publish_image: true
publish_artifact_registry: false
deploy_cloud_run: true
cloud_run_image_source: dockerhub
gcp_project_id: key-component-498805-h0
cloud_run_service: modelopslab-serving
cloud_run_region: us-central1
```

## Boundary

This change does:

```text
make Artifact Registry the default Cloud Run image source
keep Docker Hub as an explicit fallback
preserve manual deployment gating
preserve Git SHA image deployment
preserve post-deploy /health validation
```

This change does not:

```text
remove Docker Hub publishing
remove Docker Hub deployment support
remove Docker Hub secrets
trigger a live deployment after changing the default
add automatic deployment on push
```

Those are separate decisions.
