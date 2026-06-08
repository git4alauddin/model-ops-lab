# Docker Rollback Guide

This guide explains rollback for Docker images published during V8.

V8 rollback means selecting and running a previous known-good Docker image tag.

It does not yet mean rolling back a live Cloud Run service.

## Rollback Rule
Use exact Git SHA image tags for rollback.

Preferred rollback tag:

```text
<dockerhub-username>/modelopslab-serving:<git-sha>
```

Do not use `ci` as the rollback target.

Reason:

```text
ci is a moving tag
ci changes every time a new CI image is published
ci does not guarantee the exact previous image
```

Git SHA tags are stable because each tag points to one exact source commit and image build.

## Find Previous Known-Good Image
Use Docker Hub:

```text
Docker Hub
-> Repositories
-> modelopslab-serving
-> Tags
```

Find the previous known-good Git SHA tag.

Use project history to connect a tag back to a commit:

```powershell
git log --oneline
```

The commit hash should match the Docker image tag.

## Pull Previous Image Locally
Replace `<dockerhub-username>` and `<git-sha>` with real values.

```powershell
docker pull <dockerhub-username>/modelopslab-serving:<git-sha>
```

## Run Previous Image Locally
Run the selected image:

```powershell
docker run --rm -p 8000:8000 <dockerhub-username>/modelopslab-serving:<git-sha>
```

Check the API:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected result:

```text
status is ok
service is modelopslab-serving
```

## Rollback Boundary In V8
Current V8 rollback support:

```text
choose previous Git SHA image tag
pull previous image
run previous image locally
verify /health
```

Not included in V8:

```text
Cloud Run service rollback
live traffic rollback
production deployment revision rollback
post-rollback production health check
```

When Cloud Run deployment is added later, rollback will mean updating the live service back to a previous known-good image tag or Cloud Run revision.

## Safe Rollback Checklist
Before choosing a rollback image:

```text
identify the failed image tag
identify the previous known-good Git SHA tag
confirm the previous tag exists in Docker Hub
pull the previous image locally
run the previous image locally
check /health
record the rollback candidate
```

Do not overwrite or delete the failed image immediately. Keeping it available helps debugging.
