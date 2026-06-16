# Artifact Registry Setup Validation

This records the first validated Artifact Registry setup for ModelOpsLab.

This is a setup validation only. No image was pushed to Artifact Registry in this chunk.

## Validation Status

```text
status: successful
date: 2026-06-17
validation method: gcloud CLI after GUI setup
```

## API Validation

Artifact Registry API is enabled:

```text
service: artifactregistry.googleapis.com
state: ENABLED
project: projects/153930851596
```

Command used:

```powershell
gcloud services list --enabled --project=key-component-498805-h0 --filter=name:artifactregistry.googleapis.com --format=json
```

## Repository Validation

Artifact Registry repository:

```text
name: projects/key-component-498805-h0/locations/us-central1/repositories/modelopslab
registryUri: us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab
format: DOCKER
mode: STANDARD_REPOSITORY
location: us-central1
encryption: Google-managed key
repository size: 0.000MB
```

Creation evidence:

```text
createTime: 2026-06-16T18:50:56.840980Z
updateTime: 2026-06-16T18:50:56.840980Z
```

Command used:

```powershell
gcloud artifacts repositories describe modelopslab --location=us-central1 --project=key-component-498805-h0 --format=json
```

## IAM Validation

Repository-level IAM binding:

```text
role: roles/artifactregistry.writer
member: serviceAccount:modelopslab-github-deployer@key-component-498805-h0.iam.gserviceaccount.com
```

Command used:

```powershell
gcloud artifacts repositories get-iam-policy modelopslab --location=us-central1 --project=key-component-498805-h0 --format=json
```

Why this matters:

```text
GitHub Actions already impersonates this service account through Workload Identity Federation
Artifact Registry Writer lets that identity push images to the repository in a later CI chunk
repository-level access keeps the scope tighter than project-wide writer access
```

## Target Image Path

Future image path:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:<git-sha>
```

For the CI workflow later, the image identity should continue to use the immutable Git SHA tag:

```text
${{ github.sha }}
```

## Security Notes

The setup keeps the same credential posture as the Cloud Run deployment work:

```text
no service account key JSON
GitHub Actions uses Workload Identity Federation
the deploy service account receives repository-level Artifact Registry Writer
```

No secret values were recorded.

## Current Boundary

Validated:

```text
Artifact Registry API is enabled
Docker repository exists
repository is in us-central1
repository URI is known
GitHub deploy service account can write to the repository
```

Not done yet:

```text
configure Docker auth in CI
push image to Artifact Registry
deploy Cloud Run from Artifact Registry
remove Docker Hub from the deploy path
validate live /health after Artifact Registry deployment
```

## Next Chunk Direction

The next engineering chunk should update GitHub Actions to support Artifact Registry publishing behind a manual gate.

Expected direction:

```text
tests
-> Docker image build
-> Workload Identity Federation auth
-> configure Docker for us-central1-docker.pkg.dev
-> push Git SHA image to Artifact Registry
-> keep Cloud Run deployment opt-in
```

That publish gate is documented here:

```text
docs/deployment/artifact_registry_publish_gate.md
```
