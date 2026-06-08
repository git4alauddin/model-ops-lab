# V8 Commit Log

## cfb518a - v8-c1: add Docker serving image foundation

### What Changed
- Added Dockerfile for the FastAPI serving API.
- Added Docker build context exclusions with `.dockerignore`.
- Added focused Docker foundation tests.
- Added V8 documentation scaffold.
- Added a minimal README Docker serving entry point.

### What Problem It Solved
- Creates the first reproducible container boundary for the serving API.
- Prevents local runtime artifacts, logs, MLflow state, model registry files, virtual environments, and secrets from being baked into the image.

### Verification
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py` passed: `5 passed in 0.05s`.
- `python -m pytest -q` passed: `304 passed in 7.00s`.
- `docker --version` printed `Docker version 29.2.1, build a5c7197`.
- `docker build -f deployment/Dockerfile -t modelopslab-serving:v8-c1 .` built successfully.
- `docker run --rm modelopslab-serving:v8-c1 python -c "from app.serve_api import app; print(app.title); print(app.version)"` printed `ModelOpsLab Serving API` and `v7`.
- `git diff --check` passed with CRLF normalization warnings only.

## 5150b87 - v8-c2: add Docker Compose serving runtime

### What Changed
- Added Docker Compose runtime for the serving API.
- Built the service from `deployment/Dockerfile`.
- Added local port mapping for `8000:8000`.
- Mounted local `model_registry/` and `mlruns/` read-only.
- Mounted local `logs/` as writable output.
- Added focused Docker Compose runtime tests.
- Updated README and V8 docs.

### What Problem It Solved
- Replaces manual `docker run` flags with a repeatable local runtime definition.
- Defines how the containerized serving API receives local model metadata, MLflow artifacts, and log output.

### Verification
- `python -m pytest -q tests\test_v8_c2_docker_compose_runtime.py` passed: `6 passed in 0.07s`.
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py` passed: `11 passed in 0.09s`.
- `docker compose -f deployment/docker-compose.yaml config` resolved the service, build context, port mapping, and runtime mounts successfully.
- `docker compose -f deployment/docker-compose.yaml build` built `modelopslab-serving:v8-c2` successfully.
- `docker compose -f deployment/docker-compose.yaml run --rm modelopslab-serving python -c "from app.serve_api import app; print(app.title); print(app.version)"` printed `ModelOpsLab Serving API` and `v7`.
- Compose runtime `/health` check returned `{"status":"ok","service":"modelopslab-serving","api_version":"v7"}`.
- `python -m pytest -q` passed: `310 passed in 20.96s`.
- `git diff --check` passed with CRLF normalization warnings only.

## b1ab305 - v8-c3: add serving environment configuration

### What Changed
- Added typed serving runtime settings.
- Documented serving environment variables in `.env.example`.
- Updated Docker startup to use `SERVING_HOST`, `SERVING_PORT`, and `LOG_LEVEL`.
- Updated Docker Compose to pass serving environment variables.
- Updated API routes to use configured registry, MLflow, prediction log, and app log paths.
- Added focused serving environment configuration tests.
- Updated affected V7 route tests for configured route calls.
- Updated V8 docs.

### What Problem It Solved
- Makes local, Docker, Compose, and future CI/CD serving runtime behavior explicit.
- Prevents hidden environment assumptions around registry paths, MLflow paths, and log paths.

### Verification
- `python -m pytest -q tests\test_v8_c3_serving_environment_config.py` passed: `6 passed in 0.08s`.
- `python -m pytest -q tests\test_v7_c2_readiness_endpoint.py tests\test_v7_c6_predict_endpoint.py tests\test_v7_c7_prediction_logging.py tests\test_v7_c8_batch_prediction_endpoint.py tests\test_v7_c9_serving_runtime_logging.py` passed: `28 passed in 1.22s`.
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py tests\test_v8_c3_serving_environment_config.py` passed: `17 passed in 0.12s`.
- `docker compose -f deployment/docker-compose.yaml --env-file .env.example config` resolved environment variables, port mapping, and runtime mounts successfully.
- `docker compose -f deployment/docker-compose.yaml --env-file .env.example build` built `modelopslab-serving:v8-c3` successfully.
- Compose settings import check printed `local`, `0.0.0.0`, `8000`, `/app/model_registry`, `/app/mlruns`, `/app/logs/predictions.jsonl`, and `/app/logs/modelopslab.log`.
- Environment-aware Compose runtime `/health` check returned `{"status":"ok","service":"modelopslab-serving","api_version":"v7"}`.
- `python -m pytest -q` passed: `316 passed in 5.85s`.
- `git diff --check` passed with CRLF normalization warnings only.

## 4bd5652 - v8-c4: add CI test workflow

### What Changed
- Added GitHub Actions CI workflow.
- Configured CI for pushes to `main`.
- Configured CI for pull requests targeting `main`.
- Set up Python `3.11`.
- Installed dependencies from `requirements.txt`.
- Ran the full test suite with `python -m pytest -q`.
- Added focused static workflow tests.
- Updated V8 docs.

### What Problem It Solved
- Creates the first automated quality gate before Docker image build and deployment automation.
- Makes test execution visible on GitHub after pushes and pull requests.

### Verification
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py` passed: `7 passed in 0.07s`.
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py tests\test_v8_c3_serving_environment_config.py tests\test_v8_c4_ci_workflow.py` passed: `24 passed in 0.16s`.
- `python -m pytest -q` passed: `323 passed in 5.76s`.
- `git diff --check` passed with CRLF normalization warnings only.

## 6099ee6 - v8-c5: add CI Docker image build gate

### What Changed
- Added a `docker-image` job to GitHub Actions CI.
- Made the Docker image job depend on the test job.
- Built the serving image from `deployment/Dockerfile`.
- Tagged the CI build as `modelopslab-serving:ci`.
- Avoided Docker Hub login and image push.
- Added focused static workflow tests for the Docker build gate.
- Updated V8 docs.

### What Problem It Solved
- Proves the Docker serving image can build in CI after tests pass.
- Adds the next deployment safety gate before image publishing or deployment automation.

### Verification
- `python -m pytest -q tests\test_v8_c5_ci_docker_build.py` passed: `5 passed in 0.06s`.
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py` passed: `12 passed in 0.11s`.
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py tests\test_v8_c3_serving_environment_config.py tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py` passed: `29 passed in 0.18s`.
- `docker build -f deployment/Dockerfile -t modelopslab-serving:ci .` built successfully.
- `python -m pytest -q` passed: `328 passed in 5.55s`.
- `git diff --check` passed with CRLF normalization warnings only.

## 5a00187 - v8-c6: add Docker image versioning contract

### What Changed
- Added Docker image tagging contract documentation.
- Documented CI, Git SHA, semantic release, and optional `latest` tags.
- Updated CI Docker build to tag `modelopslab-serving:ci`.
- Updated CI Docker build to also tag `modelopslab-serving:${{ github.sha }}`.
- Kept Docker Hub login and image push out of CI.
- Added focused tests for image versioning behavior.
- Updated V8 docs.

### What Problem It Solved
- Makes CI image builds traceable to source commits.
- Prepares the project for rollback-safe Docker Hub publishing.
- Avoids relying on `latest` as the only image identity.

### Verification
- `python -m pytest -q tests\test_v8_c6_image_versioning.py` passed: `6 passed in 0.06s`.
- `python -m pytest -q tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py` passed: `11 passed in 0.10s`.
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py tests\test_v8_c3_serving_environment_config.py tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py` passed: `35 passed in 0.19s`.
- `docker build -f deployment/Dockerfile -t modelopslab-serving:ci -t modelopslab-serving:local-sha .` built both tags successfully.
- `python -m pytest -q` passed: `334 passed in 5.92s`.
- `git diff --check` passed with CRLF normalization warnings only.

## 418b0a5 - v8-c7: add manual CI run guide

### What Changed
- Added manual CI run guide.
- Documented when to run CI manually.
- Documented GitHub Actions UI trigger path.
- Explained the `tests` job and `docker-image` job.
- Explained how to inspect pytest and Docker build failures.
- Documented that Docker Hub push and deployment are not implemented yet.
- Added focused guide tests.
- Updated V8 docs.

### What Problem It Solved
- Makes manual CI operation repeatable and clear.
- Prevents the manual trigger strategy from becoming tribal knowledge.

### Verification
- `python -m pytest -q tests\test_v8_c7_ci_manual_run_guide.py` passed: `5 passed in 0.05s`.
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py tests\test_v8_c7_ci_manual_run_guide.py` passed: `23 passed in 0.18s`.
- `python -m pytest -q` passed: `339 passed in 5.81s`.
- `git diff --check` passed with CRLF normalization warnings only.

## 447e0b8 - v8-c8: add Docker Hub publishing plan

### What Changed
- Added Docker Hub publishing plan.
- Documented target image naming.
- Documented required GitHub Actions secrets.
- Documented Docker Hub token usage instead of password.
- Documented planned CI and Git SHA push tags.
- Documented GitHub UI path for adding repository secrets.
- Added tests that verify CI still does not login or push.
- Updated README and V8 docs.

### What Problem It Solved
- Prepares registry publishing safely before credentials are introduced.
- Keeps Docker Hub push out of CI until the secret and naming contract is clear.

### Verification
- `python -m pytest -q tests\test_v8_c8_dockerhub_publishing_plan.py` passed: `6 passed in 0.05s`.
- `python -m pytest -q tests\test_v8_c7_ci_manual_run_guide.py tests\test_v8_c8_dockerhub_publishing_plan.py` passed: `11 passed in 0.06s`.
- `python -m pytest -q` passed: `345 passed in 5.92s`.
- `git diff --check` passed with CRLF normalization warnings only.

## fbd97c3 - v8-c9: add Docker Hub secrets setup guide

### What Changed
- Added Docker Hub secrets setup guide.
- Documented Docker Hub access token creation.
- Documented GitHub Actions repository secret creation.
- Documented required secret names.
- Documented token usage instead of password.
- Documented safe verification without exposing values.
- Added focused tests for the secrets guide and no-push CI boundary.
- Updated README and V8 docs.

### What Problem It Solved
- Makes credential setup safe and repeatable before CI consumes Docker Hub secrets.
- Keeps Docker Hub publishing separate from secret preparation.

### Verification
- `python -m pytest -q tests\test_v8_c9_dockerhub_secrets_setup.py` passed: `6 passed in 0.05s`.
- `python -m pytest -q tests\test_v8_c8_dockerhub_publishing_plan.py tests\test_v8_c9_dockerhub_secrets_setup.py` passed: `12 passed in 0.07s`.
- `python -m pytest -q` passed: `351 passed in 5.99s`.
- `git diff --check` passed with CRLF normalization warnings only.

## 624c69f - v8-c10: add manual Docker Hub publish gate

### What Changed
- Added manual `publish_image` workflow input.
- Kept `publish_image` default as `false`.
- Added Docker Hub login, tag, and push steps behind the manual publish condition.
- Pushes Git SHA and `ci` image tags when publishing is enabled.
- Added Docker Hub publish run guide.
- Updated related V8 tests for the guarded-publish contract.
- Updated README, deployment docs, and V8 docs.

### What Problem It Solved
- Enables Docker Hub publishing without making every CI validation run publish an image.
- Keeps publishing explicit and manual during the deployment learning phase.

### Verification
- `python -m pytest -q tests\test_v8_c10_dockerhub_publish_gate.py` passed: `7 passed in 0.08s`.
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py tests\test_v8_c8_dockerhub_publishing_plan.py tests\test_v8_c9_dockerhub_secrets_setup.py tests\test_v8_c10_dockerhub_publish_gate.py` passed: `37 passed in 0.26s`.
- `python -m pytest -q` passed: `358 passed in 5.68s`.
- `git diff --check` passed with CRLF normalization warnings only.

## 1640824 - fix: validate Docker Hub secrets before login

### What Changed
- Added a Docker Hub secret validation step before Docker Hub login.
- Added clear missing-secret errors for `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`.
- Added troubleshooting guidance to the Docker Hub publish run guide.
- Added a complete Docker Hub credentials walkthrough.
- Updated tests for the preflight behavior.

### What Problem It Solved
- Replaces the generic Docker login username/password required error with a project-specific missing-secret message.

### Verification
- `python -m pytest -q tests\test_v8_c9_dockerhub_secrets_setup.py tests\test_v8_c10_dockerhub_publish_gate.py` passed: `14 passed in 0.11s`.
- `python -m pytest -q` passed: `359 passed in 6.04s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c10_dockerhub_publish_gate.py tests\test_v8_c9_dockerhub_secrets_setup.py` passed: `15 passed in 0.13s`.
- `python -m pytest -q` passed: `360 passed in 5.84s`.
- `git diff --check` passed with CRLF normalization warnings only.

## 1f870b0 - v8-c11: record Docker Hub publish validation

### What Changed
- Added Docker Hub publish validation record.
- Documented completed Docker Hub repository configuration.
- Documented completed GitHub Actions secret configuration.
- Documented successful manual publish path.
- Documented expected Docker Hub tags.
- Clarified that V8 validates image publishing but does not deploy to a live cloud runtime.
- Added focused validation tests.

### What Problem It Solved
- Records the external Docker Hub configuration and publish validation inside the project docs.
- Separates registry publishing from actual cloud deployment.

### Verification
- `python -m pytest -q tests\test_v8_c11_dockerhub_publish_validation.py` passed: `5 passed in 0.05s`.
- `python -m pytest -q tests\test_v8_c9_dockerhub_secrets_setup.py tests\test_v8_c10_dockerhub_publish_gate.py tests\test_v8_c11_dockerhub_publish_validation.py` passed: `20 passed in 0.13s`.
- `python -m pytest -q` passed: `365 passed in 8.68s`.
- `git diff --check` passed with CRLF normalization warnings only.

## 31e6373 - v8-c12: add Docker rollback guide

### What Changed
- Added Docker rollback guide.
- Documented rollback with exact Git SHA image tags.
- Warned against using the moving `ci` tag for rollback.
- Documented how to find previous known-good image tags.
- Documented local `docker pull`, `docker run`, and `/health` rollback checks.
- Clarified that live Cloud Run rollback is outside current V8 scope.
- Added focused rollback guide tests.

### What Problem It Solved
- Gives V8 a clear rollback rule for published Docker images.
- Separates image-level rollback readiness from future live service rollback.

### Verification
- `python -m pytest -q tests\test_v8_c12_docker_rollback_guide.py` passed: `5 passed in 0.04s`.
- `python -m pytest -q tests\test_v8_c11_dockerhub_publish_validation.py tests\test_v8_c12_docker_rollback_guide.py` passed: `10 passed in 0.06s`.
- `python -m pytest -q` passed: `370 passed in 5.33s`.
- `git diff --check` passed with CRLF normalization warnings only.

## Pending - v8-c13: add Cloud Run deployment foundation guide

### What Changed
- Added Cloud Run deployment foundation guide.
- Documented why Cloud Run is the first GCP deployment target.
- Documented Docker Hub versus Artifact Registry tradeoff.
- Documented Google Cloud Console deployment flow.
- Documented service name, region, port, access, and environment variable guidance.
- Documented `/health` validation after deployment.
- Documented that GitHub Actions GCP deployment automation is later scope.
- Added focused Cloud Run guide tests.

### What Problem It Solved
- Defines where the V8 Docker image can run on GCP.
- Separates manual Cloud Run deployment learning from later CI/CD deployment automation.

### Verification
- `python -m pytest -q tests\test_v8_c13_cloud_run_deployment_foundation.py` passed: `6 passed in 0.06s`.
- `python -m pytest -q tests\test_v8_c12_docker_rollback_guide.py tests\test_v8_c13_cloud_run_deployment_foundation.py` passed: `11 passed in 0.06s`.
- `python -m pytest -q` passed: `376 passed in 7.35s`.
- `git diff --check` passed with CRLF normalization warnings only.
