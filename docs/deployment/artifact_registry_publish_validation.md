# Artifact Registry Publish Validation

This records the first live validation of the GitHub Actions Artifact Registry publish gate for ModelOpsLab.

This validation published an image to Artifact Registry only. It did not deploy Cloud Run from Artifact Registry.

## Validation Status

```text
status: successful
date: 2026-06-17
workflow run: 27641517665
workflow URL: https://github.com/git4alauddin/model-ops-lab/actions/runs/27641517665
trigger: workflow_dispatch
```

GitHub run timestamps were recorded in UTC:

```text
createdAt: 2026-06-16T19:09:05Z
updatedAt: 2026-06-16T19:12:20Z
```

## Workflow Inputs

```text
publish_image: false
publish_artifact_registry: true
deploy_cloud_run: false
gcp_project_id: key-component-498805-h0
artifact_registry_location: us-central1
artifact_registry_repository: modelopslab
```

Why this input set was used:

```text
validate Artifact Registry publishing alone
avoid Docker Hub publishing in this run
avoid Cloud Run deployment in this run
```

## Source Commit

```text
commit: 55464a7e17ba6833673ddf897b6284fc772333df
short commit: 55464a7
message: v8-c19: add Artifact Registry publish gate
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
cloud run deploy: skipped
```

Job IDs:

```text
pytest: 81742496009
docker image build: 81742733568
cloud run deploy: 81743136007
```

Docker Hub steps were skipped:

```text
Validate Docker Hub secrets: skipped
Login to Docker Hub: skipped
Tag Docker Hub image: skipped
Push Docker Hub image: skipped
```

Artifact Registry steps succeeded:

```text
Validate Artifact Registry inputs: success
Authenticate to Google Cloud for Artifact Registry: success
Set up Google Cloud SDK: success
Configure Docker for Artifact Registry: success
Tag Artifact Registry image: success
Push Artifact Registry image: success
```

## Artifact Registry Image Evidence

Package:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving
```

Published tag:

```text
55464a7e17ba6833673ddf897b6284fc772333df
```

Full image reference:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:55464a7e17ba6833673ddf897b6284fc772333df
```

Digest:

```text
sha256:b073b2bdd44249ee6a3de10abb8d96035c391170d338850dabc0393a5a5e84f2
```

Artifact Registry metadata:

```text
createTime: 2026-06-16T19:12:16.988207Z
updateTime: 2026-06-16T19:12:16.988207Z
buildTime: 2026-06-16T19:11:23.564716369Z
imageSizeBytes: 332707074
mediaType: application/vnd.docker.distribution.manifest.v2+json
```

Command used:

```powershell
gcloud artifacts docker images list us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab --include-tags --format=json
```

## Boundary Confirmed

Validated:

```text
manual publish_artifact_registry input works
tests still gate image build
Workload Identity Federation auth works for Artifact Registry publishing
gcloud Docker auth works for us-central1-docker.pkg.dev
Git SHA image is pushed to Artifact Registry
Docker Hub publishing can stay disabled for this path
Cloud Run deployment can stay disabled for this path
```

Not done yet:

```text
deploy Cloud Run from Artifact Registry
validate /health from an Artifact Registry deployed revision
remove Docker Hub deployment path
remove Docker Hub secrets
```

## Next Chunk Direction

The next deployment chunk can switch the manually gated Cloud Run deployment image from Docker Hub to Artifact Registry.

Expected direction:

```text
publish_artifact_registry=true
deploy_cloud_run=true
cloud_run_image_source=artifact_registry
Cloud Run image: us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:<git-sha>
post-deploy /health validation
```

The image source gate is documented here:

```text
docs/deployment/cloud_run_image_source_gate.md
```
