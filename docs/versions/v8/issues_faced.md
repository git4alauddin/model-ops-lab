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

## CI Trigger Strategy

### Issue
The CI workflow was running on every push, which is wasteful during small iterative learning commits.

### Resolution
Changed the workflow trigger to `workflow_dispatch` so CI runs only when manually requested from GitHub Actions.

### Issue
Changing the trigger could accidentally weaken CI coverage.

### Resolution
Kept the existing test and Docker image build jobs unchanged, and updated workflow tests to verify only the trigger strategy changed.

## V8-C7: Manual CI Run Guide

### Issue
After switching CI to manual execution, the project needed clear instructions for when and how to run the workflow.

### Resolution
Added a manual CI run guide that documents the GitHub Actions UI flow, the workflow jobs, failure inspection, and the current no-push boundary.

## V8-C8: Docker Hub Publishing Plan

### Issue
The project was close to registry publishing, but Docker Hub credentials and image naming rules were not documented.

### Resolution
Added a Docker Hub publishing plan with target image names, required GitHub secrets, token guidance, planned tags, and the current no-push boundary.

### Issue
Adding Docker Hub login too early would mix secret handling with registry planning.

### Resolution
Kept CI unchanged for publishing and added tests that verify no Docker login or push exists yet.

## V8-C9: Docker Hub Secrets Setup Guide

### Issue
Docker Hub publishing needs credentials, but adding `docker login` before documenting secret setup would make the workflow harder to operate safely.

### Resolution
Added a secrets setup guide that documents Docker Hub token creation, GitHub Actions repository secrets, safe verification, and the current no-push CI boundary.

## V8-C10: Manual Docker Hub Publish Gate

### Issue
Adding Docker Hub push directly to the workflow could publish images on every manual validation run.

### Resolution
Added a `publish_image` workflow input that defaults to `false`, and guarded Docker Hub login, tag, and push steps behind `publish_image == true`.

### Issue
Existing tests asserted that no Docker Hub publish steps existed anywhere in CI.

### Resolution
Updated those tests to verify the new guarded-publish contract instead of the old no-push boundary.

### Issue
Manual publishing reached Docker Hub login, but GitHub Actions raised a username/password required error when secrets were missing or unavailable.

### Resolution
Added a Docker Hub secret preflight step before login. The workflow now fails with a clear message when `DOCKERHUB_USERNAME` or `DOCKERHUB_TOKEN` is missing.

## V8-C11: Docker Hub Publish Validation

### Issue
The project had the Docker Hub publish workflow implemented, but the repo did not yet record that the external Docker Hub repository, GitHub secrets, and manual publish run were validated.

### Resolution
Added a Docker Hub publish validation record that documents the completed external configuration, successful manual publish path, expected tags, and V8's no-cloud-deployment boundary.

## V8-C12: Docker Rollback Guide

### Issue
Docker images were being published with both Git SHA and `ci` tags, but rollback behavior was not documented.

### Resolution
Added a Docker rollback guide that makes Git SHA tags the rollback target, warns against using the moving `ci` tag, and documents local rollback verification before live Cloud Run deployment exists.

## V8-C13: Cloud Run Deployment Foundation

### Issue
Docker Hub publishing was validated, but the project did not yet document where the container would actually run on GCP.

### Resolution
Added a Cloud Run deployment foundation guide that documents the manual Google Cloud Console path, service settings, Docker Hub versus Artifact Registry tradeoff, `/health` validation, and the boundary before CI-based GCP deployment automation.
