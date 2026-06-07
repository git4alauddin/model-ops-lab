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

## V8-C4: CI Test Workflow

### Issue
Tests were still manually triggered after code changes.

### Resolution
Added a GitHub Actions workflow that installs dependencies and runs the full pytest suite on pushes and pull requests.

### Issue
CI YAML can silently drift from the intended quality gate.

### Resolution
Added static workflow tests that verify triggers, Python setup, dependency installation, and pytest execution.

## V8-C5: CI Docker Image Build Gate

### Issue
CI could run tests, but it did not yet prove that the Docker serving image can build from the repository state.

### Resolution
Added a Docker image build job that runs after the test job and builds `deployment/Dockerfile`.

### Issue
Image publishing would require Docker Hub credentials and should not be mixed with the first build gate.

### Resolution
Kept V8-C5 limited to `docker build` only. Docker login and push are intentionally left for a later chunk.

## V8-C6: Docker Image Versioning Contract

### Issue
CI could build a Docker image, but the image tag was only a generic `ci` tag.

### Resolution
Added a documented image tagging contract and updated CI to produce both `modelopslab-serving:ci` and `modelopslab-serving:${{ github.sha }}`.

### Issue
Using `latest` as the only tag would make rollback and source traceability weak.

### Resolution
Documented that `latest` is optional convenience only and must not be the only deployed or rollback tag.
