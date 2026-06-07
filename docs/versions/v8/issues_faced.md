# V8 Issues Faced

## Open
No open V8 issues.

## V8-C1: Docker Serving Image Foundation

### Issue
The V7 serving API worked locally, but it still depended on the developer machine and local virtual environment.

### Resolution
Added a Dockerfile and `.dockerignore` so the serving API has a reproducible image boundary while keeping local runtime state outside the image.

## V8-C2: Docker Compose Serving Runtime

### Issue
The Docker image could build, but running it still required manual `docker run` flags and did not define how local serving runtime state should be attached.

### Resolution
Added Docker Compose with explicit port mapping and runtime mounts for local model registry metadata, MLflow artifacts, and logs.

## V8-C3: Serving Environment Configuration

### Issue
The container runtime worked, but important serving settings were still implicit.

### Resolution
Added typed serving settings, documented environment variables, and wired Docker Compose plus API routes to the same runtime configuration contract.

### Issue
The first environment-aware Compose runtime check failed because Uvicorn rejected uppercase `INFO` as a log level.

### Resolution
Changed the deployment-facing `LOG_LEVEL` default to lowercase `info` while keeping Python settings normalized to uppercase internally.
