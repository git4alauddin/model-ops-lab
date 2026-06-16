# Artifact Registry Foundation

This guide prepares the next deployment boundary for ModelOpsLab: moving the serving image from Docker Hub to Google Artifact Registry.

This chunk is setup and learning only. It does not change GitHub Actions yet.

## Why Artifact Registry Is Next

The first live Cloud Run deployment used Docker Hub:

```text
GitHub Actions
-> Docker Hub
-> Cloud Run
```

That worked, but the first Cloud Run deploy attempt failed because the fresh public Docker Hub tag was not immediately available through Google's pull path.

Artifact Registry gives a GCP-native path:

```text
GitHub Actions
-> Artifact Registry
-> Cloud Run
```

Why this is better:

```text
image storage is inside Google Cloud
IAM controls image push and pull
Cloud Run and the registry live in the same cloud boundary
Docker Hub mirror timing is removed from the critical path
```

## Current Project Values

```text
GCP project ID: key-component-498805-h0
GCP project number: 153930851596
Cloud Run region: us-central1
Cloud Run service: modelopslab-serving
GitHub deploy service account: modelopslab-github-deployer@key-component-498805-h0.iam.gserviceaccount.com
```

Recommended Artifact Registry repository:

```text
Repository name: modelopslab
Format: Docker
Mode: Standard
Location type: Region
Region: us-central1
```

Recommended image path:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:<git-sha>
```

Image path shape:

```text
LOCATION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE:TAG
```

## GUI Setup Steps

Use the Google Cloud Console.

### Enable Artifact Registry API

Path:

```text
Google Cloud Console
-> APIs & Services
-> Library
-> Artifact Registry API
-> Enable
```

If it is already enabled, leave it as-is.

### Create Docker Repository

Path:

```text
Google Cloud Console
-> Artifact Registry
-> Repositories
-> Create Repository
```

Use:

```text
Name: modelopslab
Format: Docker
Mode: Standard
Location type: Region
Region: us-central1
Encryption: Google-managed encryption key
Cleanup policies: leave empty for the first setup
```

Why same region as Cloud Run:

```text
keeps image storage close to the Cloud Run service
keeps the first migration simple
reduces cross-region surprises
```

## IAM Needed

GitHub Actions currently impersonates:

```text
modelopslab-github-deployer@key-component-498805-h0.iam.gserviceaccount.com
```

For Artifact Registry publishing, that service account needs write access to the repository.

Recommended role:

```text
Artifact Registry Writer
roles/artifactregistry.writer
```

Grant it at repository level if possible:

```text
Artifact Registry
-> Repositories
-> modelopslab
-> Permissions
-> Grant access
-> Principal: modelopslab-github-deployer@key-component-498805-h0.iam.gserviceaccount.com
-> Role: Artifact Registry Writer
```

Repository-level access is tighter than project-wide access.

Cloud Run also needs permission to read the deployed image. In the same project, this is commonly already covered by default service-agent behavior, but the explicit role to remember is:

```text
Artifact Registry Reader
roles/artifactregistry.reader
```

If the registry and Cloud Run service are ever split across projects, the Cloud Run service agent must receive Artifact Registry Reader on the image repository.

## Local Docker Auth Concept

Artifact Registry Docker hosts use this pattern:

```text
LOCATION-docker.pkg.dev
```

For this project:

```text
us-central1-docker.pkg.dev
```

Local Docker authentication command:

```powershell
gcloud auth configure-docker us-central1-docker.pkg.dev
```

This updates Docker's credential helper configuration so Docker can push and pull images from that Artifact Registry host.

This is a local developer setup step. GitHub Actions will use Workload Identity Federation and GCP credentials when we automate publishing later.

## Future GitHub Actions Direction

Current Docker Hub image:

```text
docker.io/${{ secrets.DOCKERHUB_USERNAME }}/modelopslab-serving:${{ github.sha }}
```

Future Artifact Registry image:

```text
us-central1-docker.pkg.dev/key-component-498805-h0/modelopslab/modelopslab-serving:${{ github.sha }}
```

Future workflow behavior should be:

```text
tests
-> Docker image build
-> authenticate to GCP with Workload Identity Federation
-> configure Docker for us-central1-docker.pkg.dev
-> tag image with Artifact Registry path
-> push Git SHA image to Artifact Registry
-> deploy that Artifact Registry image to Cloud Run
-> validate /health
```

Docker Hub secrets should no longer be required once the workflow fully moves to Artifact Registry.

## GUI Checkpoints

After setup, verify:

```text
Artifact Registry repository exists
repository format is Docker
repository location is us-central1
service account has Artifact Registry Writer
no service account key JSON was created
```

After a future push, verify:

```text
image name appears in the repository
Git SHA tag appears
image digest appears
last pushed timestamp is current
```

After a future Cloud Run deployment, verify:

```text
Cloud Run revision image points to us-central1-docker.pkg.dev
/health returns status ok
traffic is on the expected revision
```

## Boundaries

This foundation does not:

```text
create the Artifact Registry repository automatically
grant IAM automatically
change GitHub Actions
remove Docker Hub support
push an image to Artifact Registry
deploy from Artifact Registry
validate a live Artifact Registry deployment
```

Those are separate chunks.

## Source References

- Artifact Registry Docker quickstart: https://cloud.google.com/artifact-registry/docs/docker/store-docker-container-images
- Artifact Registry Docker authentication: https://cloud.google.com/artifact-registry/docs/docker/authentication
- Artifact Registry IAM access control: https://cloud.google.com/artifact-registry/docs/access-control
- Cloud Run container image deployment: https://cloud.google.com/run/docs/deploying
