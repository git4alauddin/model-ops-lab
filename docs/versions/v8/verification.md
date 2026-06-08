# V8 Verification

## Checks Performed
- Verified Dockerfile exists.
- Verified Dockerfile uses a Python slim runtime image.
- Verified Dockerfile installs project requirements.
- Verified Dockerfile starts `app.serve_api:app` through Uvicorn.
- Verified Dockerfile exposes port `8000`.
- Verified `.dockerignore` exists.
- Verified `.dockerignore` excludes local runtime state, secrets, virtual environment, and caches.
- Verified source code, configs, and requirements remain available to the Docker build context.
- Verified Docker Compose file exists.
- Verified Docker Compose defines the serving service.
- Verified Docker Compose builds from `deployment/Dockerfile`.
- Verified Docker Compose exposes port `8000`.
- Verified Docker Compose mounts local serving runtime state.
- Verified Docker Compose leaves app startup owned by the Dockerfile.
- Verified serving settings use local-safe defaults.
- Verified serving settings accept environment overrides.
- Verified invalid serving ports are rejected.
- Verified `.env.example` documents serving runtime keys.
- Verified Docker Compose passes serving environment variables.
- Verified Dockerfile uses serving environment variables for Uvicorn startup.
- Verified API routes use configured registry, MLflow, prediction log, and app log paths.
- Verified CI workflow exists.
- Verified CI workflow uses manual trigger only.
- Verified CI workflow checks out the repository.
- Verified CI workflow sets up Python `3.11`.
- Verified CI workflow installs `requirements.txt`.
- Verified CI workflow runs `python -m pytest -q`.
- Verified CI Docker image build job exists.
- Verified CI Docker image build job runs after tests.
- Verified CI Docker image build uses `deployment/Dockerfile`.
- Verified CI Docker image build tags `modelopslab-serving:ci`.
- Verified CI workflow does not log in to Docker Hub or push an image.
- Verified Docker image tagging contract exists.
- Verified image tagging contract documents CI, Git SHA, semantic release, and optional latest tags.
- Verified image tagging contract warns against latest-only rollback.
- Verified CI Docker image build also tags images with `${{ github.sha }}`.
- Verified CI Docker image versioning still avoids Docker Hub login and push.
- Verified CI workflow no longer runs automatically on push.
- Verified CI workflow no longer runs automatically on pull request.
- Verified manual CI run guide exists.
- Verified manual CI run guide documents `workflow_dispatch`.
- Verified manual CI run guide documents the GitHub Actions UI path.
- Verified manual CI run guide explains `tests` and `docker-image` jobs.
- Verified manual CI run guide states Docker Hub push is not implemented yet.
- Verified Docker Hub publishing plan exists.
- Verified Docker Hub publishing plan documents required secrets.
- Verified Docker Hub publishing plan requires token instead of password.
- Verified Docker Hub publishing plan documents image name format.
- Verified Docker Hub publishing plan documents GitHub secret UI path.
- Verified CI workflow still does not publish to Docker Hub.
- Verified Docker Hub secrets setup guide exists.
- Verified Docker Hub secrets setup guide documents access token creation.
- Verified Docker Hub secrets setup guide documents GitHub Actions repository secrets.
- Verified Docker Hub secrets setup guide documents safe secret verification.
- Verified Docker Hub secrets setup guide discourages passwords and token exposure.
- Verified CI workflow still has no Docker Hub login or push steps.
- Verified CI workflow keeps manual trigger only.
- Verified `publish_image` input defaults to `false`.
- Verified Docker Hub login uses GitHub Actions secrets.
- Verified Docker Hub secrets are validated before Docker Hub login.
- Verified Docker Hub login runs only when `publish_image` is `true`.
- Verified Docker Hub push runs only when `publish_image` is `true`.
- Verified Docker Hub push includes Git SHA and `ci` tags.
- Verified tests still gate Docker image build and publish.
- Verified Docker Hub publish run guide documents the GitHub Actions UI flow.
- Verified Docker Hub publish validation record exists.
- Verified Docker Hub publish validation records completed manual publish.
- Verified Docker Hub publish validation records required external configuration.
- Verified Docker Hub publish validation documents published tags.
- Verified Docker Hub publish validation keeps live cloud deployment out of V8 scope.
- Verified Docker rollback guide exists.
- Verified Docker rollback guide documents Git SHA rollback.
- Verified Docker rollback guide warns against `ci` rollback.
- Verified Docker rollback guide documents local pull and run commands.
- Verified Docker rollback guide keeps Cloud Run rollback out of V8 scope.
- Verified Cloud Run deployment foundation guide exists.
- Verified Cloud Run guide documents Cloud Run as target.
- Verified Cloud Run guide documents Docker Hub versus Artifact Registry tradeoff.
- Verified Cloud Run guide documents Google Cloud Console deployment flow.
- Verified Cloud Run guide documents service settings and environment variables.
- Verified Cloud Run guide documents `/health` validation.
- Verified current CI workflow does not deploy to GCP yet.

## Commands Executed
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py`
- `python -m pytest -q`
- `docker --version`
- `docker build -f deployment/Dockerfile -t modelopslab-serving:v8-c1 .`
- `docker run --rm modelopslab-serving:v8-c1 python -c "from app.serve_api import app; print(app.title); print(app.version)"`
- `python -m pytest -q tests\test_v8_c2_docker_compose_runtime.py`
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py`
- `docker compose -f deployment/docker-compose.yaml config`
- `docker compose -f deployment/docker-compose.yaml build`
- `docker compose -f deployment/docker-compose.yaml run --rm modelopslab-serving python -c "from app.serve_api import app; print(app.title); print(app.version)"`
- `docker compose -f deployment/docker-compose.yaml up -d --build`
- `Invoke-RestMethod http://127.0.0.1:8000/health`
- `docker compose -f deployment/docker-compose.yaml down`
- `python -m pytest -q tests\test_v8_c3_serving_environment_config.py`
- `python -m pytest -q tests\test_v7_c2_readiness_endpoint.py tests\test_v7_c6_predict_endpoint.py tests\test_v7_c7_prediction_logging.py tests\test_v7_c8_batch_prediction_endpoint.py tests\test_v7_c9_serving_runtime_logging.py`
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py tests\test_v8_c3_serving_environment_config.py`
- `docker compose -f deployment/docker-compose.yaml --env-file .env.example config`
- `docker compose -f deployment/docker-compose.yaml --env-file .env.example build`
- `docker compose -f deployment/docker-compose.yaml --env-file .env.example run --rm modelopslab-serving python -c "from app.serving.settings import get_serving_settings; s=get_serving_settings(); print(s.modelopslab_env); print(s.serving_host); print(s.serving_port); print(s.model_registry_dir); print(s.mlflow_runs_dir); print(s.prediction_log_path); print(s.app_log_path)"`
- `docker compose -f deployment/docker-compose.yaml --env-file .env.example up -d --build`
- `Invoke-RestMethod http://127.0.0.1:8000/health`
- `docker compose -f deployment/docker-compose.yaml --env-file .env.example down`
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py`
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py tests\test_v8_c3_serving_environment_config.py tests\test_v8_c4_ci_workflow.py`
- `python -m pytest -q tests\test_v8_c5_ci_docker_build.py`
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py`
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py tests\test_v8_c3_serving_environment_config.py tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py`
- `docker build -f deployment/Dockerfile -t modelopslab-serving:ci .`
- `python -m pytest -q tests\test_v8_c6_image_versioning.py`
- `python -m pytest -q tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py`
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py tests\test_v8_c3_serving_environment_config.py tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py`
- `docker build -f deployment/Dockerfile -t modelopslab-serving:ci -t modelopslab-serving:local-sha .`
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py`
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py`
- `python -m pytest -q tests\test_v8_c7_ci_manual_run_guide.py`
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py tests\test_v8_c7_ci_manual_run_guide.py`
- `python -m pytest -q tests\test_v8_c8_dockerhub_publishing_plan.py`
- `python -m pytest -q tests\test_v8_c7_ci_manual_run_guide.py tests\test_v8_c8_dockerhub_publishing_plan.py`
- `python -m pytest -q tests\test_v8_c9_dockerhub_secrets_setup.py`
- `python -m pytest -q tests\test_v8_c8_dockerhub_publishing_plan.py tests\test_v8_c9_dockerhub_secrets_setup.py`
- `python -m pytest -q tests\test_v8_c10_dockerhub_publish_gate.py`
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py tests\test_v8_c8_dockerhub_publishing_plan.py tests\test_v8_c9_dockerhub_secrets_setup.py tests\test_v8_c10_dockerhub_publish_gate.py`
- `python -m pytest -q tests\test_v8_c11_dockerhub_publish_validation.py`
- `python -m pytest -q tests\test_v8_c9_dockerhub_secrets_setup.py tests\test_v8_c10_dockerhub_publish_gate.py tests\test_v8_c11_dockerhub_publish_validation.py`
- `python -m pytest -q tests\test_v8_c12_docker_rollback_guide.py`
- `python -m pytest -q tests\test_v8_c11_dockerhub_publish_validation.py tests\test_v8_c12_docker_rollback_guide.py`
- `python -m pytest -q tests\test_v8_c13_cloud_run_deployment_foundation.py`
- `python -m pytest -q tests\test_v8_c12_docker_rollback_guide.py tests\test_v8_c13_cloud_run_deployment_foundation.py`
- `python -m pytest -q`
- `git diff --check`

## Expected Output
- Docker serving foundation tests pass.
- Existing test suite remains passing.
- Docker is available locally.
- Docker image builds successfully when Docker Desktop is running.
- Docker build context excludes local runtime-heavy folders.
- Dockerfile can start the FastAPI serving API inside the image.
- Built image can import the FastAPI serving app.
- Docker Compose config is valid.
- Docker Compose can build the serving image.
- Docker Compose can run the service image and import the FastAPI app.
- Docker Compose can start the serving container and expose `/health`.
- Serving environment settings are explicit and test-covered.
- Compose can resolve `.env.example` into container runtime settings.
- The environment-aware container can start and serve `/health`.
- CI workflow provides an automated test gate before Docker image build and deployment gates.
- CI workflow verifies the serving Docker image can build after tests pass.
- CI workflow does not publish images yet.
- CI workflow builds a traceable Git SHA image tag.
- Image tagging contract is documented before Docker Hub publishing.
- CI workflow can be run manually when validation is needed.
- CI workflow no longer spends GitHub Actions minutes on every push.
- Manual CI operation is documented for repeatable use from GitHub Actions.
- Docker Hub publishing is planned before registry credentials or push steps are added.
- Docker Hub secret setup is documented before Docker login or push steps are added to CI.
- Docker Hub publishing is manually gated and disabled by default.
- Docker Hub publishing has been externally configured and manually validated.
- Docker image rollback is documented around exact Git SHA image tags.
- Cloud Run deployment foundation is documented while CI-based GCP deployment remains later scope.

## Actual Output
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py` passed: `5 passed in 0.05s`.
- `python -m pytest -q` passed: `304 passed in 7.00s`.
- `docker --version` printed `Docker version 29.2.1, build a5c7197`.
- `docker build -f deployment/Dockerfile -t modelopslab-serving:v8-c1 .` built successfully.
- `docker run --rm modelopslab-serving:v8-c1 python -c "from app.serve_api import app; print(app.title); print(app.version)"` printed `ModelOpsLab Serving API` and `v7`.
- `python -m pytest -q tests\test_v8_c2_docker_compose_runtime.py` passed: `6 passed in 0.07s`.
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py` passed: `11 passed in 0.09s`.
- `docker compose -f deployment/docker-compose.yaml config` resolved the service, build context, port mapping, and runtime mounts successfully.
- `docker compose -f deployment/docker-compose.yaml build` built `modelopslab-serving:v8-c2` successfully.
- `docker compose -f deployment/docker-compose.yaml run --rm modelopslab-serving python -c "from app.serve_api import app; print(app.title); print(app.version)"` printed `ModelOpsLab Serving API` and `v7`.
- Compose runtime `/health` check returned `{"status":"ok","service":"modelopslab-serving","api_version":"v7"}`.
- `python -m pytest -q` passed: `310 passed in 20.96s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c3_serving_environment_config.py` passed: `6 passed in 0.08s`.
- `python -m pytest -q tests\test_v7_c2_readiness_endpoint.py tests\test_v7_c6_predict_endpoint.py tests\test_v7_c7_prediction_logging.py tests\test_v7_c8_batch_prediction_endpoint.py tests\test_v7_c9_serving_runtime_logging.py` passed: `28 passed in 1.22s`.
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py tests\test_v8_c3_serving_environment_config.py` passed: `17 passed in 0.12s`.
- `docker compose -f deployment/docker-compose.yaml --env-file .env.example config` resolved environment variables, port mapping, and runtime mounts successfully.
- `docker compose -f deployment/docker-compose.yaml --env-file .env.example build` built `modelopslab-serving:v8-c3` successfully.
- Compose settings import check printed `local`, `0.0.0.0`, `8000`, `/app/model_registry`, `/app/mlruns`, `/app/logs/predictions.jsonl`, and `/app/logs/modelopslab.log`.
- Environment-aware Compose runtime `/health` check returned `{"status":"ok","service":"modelopslab-serving","api_version":"v7"}`.
- `python -m pytest -q` passed: `316 passed in 5.85s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py` passed: `7 passed in 0.07s`.
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py tests\test_v8_c3_serving_environment_config.py tests\test_v8_c4_ci_workflow.py` passed: `24 passed in 0.16s`.
- `python -m pytest -q` passed: `323 passed in 5.76s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c5_ci_docker_build.py` passed: `5 passed in 0.06s`.
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py` passed: `12 passed in 0.11s`.
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py tests\test_v8_c3_serving_environment_config.py tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py` passed: `29 passed in 0.18s`.
- `docker build -f deployment/Dockerfile -t modelopslab-serving:ci .` built successfully.
- `python -m pytest -q` passed: `328 passed in 5.55s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c6_image_versioning.py` passed: `6 passed in 0.06s`.
- `python -m pytest -q tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py` passed: `11 passed in 0.10s`.
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py tests\test_v8_c2_docker_compose_runtime.py tests\test_v8_c3_serving_environment_config.py tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py` passed: `35 passed in 0.19s`.
- `docker build -f deployment/Dockerfile -t modelopslab-serving:ci -t modelopslab-serving:local-sha .` built both tags successfully.
- `python -m pytest -q` passed: `334 passed in 5.92s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py` passed: `7 passed in 0.08s`.
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py` passed: `18 passed in 0.12s`.
- `python -m pytest -q` passed: `334 passed in 6.39s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c7_ci_manual_run_guide.py` passed: `5 passed in 0.05s`.
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py tests\test_v8_c7_ci_manual_run_guide.py` passed: `23 passed in 0.18s`.
- `python -m pytest -q` passed: `339 passed in 5.81s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c8_dockerhub_publishing_plan.py` passed: `6 passed in 0.05s`.
- `python -m pytest -q tests\test_v8_c7_ci_manual_run_guide.py tests\test_v8_c8_dockerhub_publishing_plan.py` passed: `11 passed in 0.06s`.
- `python -m pytest -q tests\test_v8_c9_dockerhub_secrets_setup.py` passed: `6 passed in 0.05s`.
- `python -m pytest -q tests\test_v8_c8_dockerhub_publishing_plan.py tests\test_v8_c9_dockerhub_secrets_setup.py` passed: `12 passed in 0.07s`.
- `python -m pytest -q` passed: `351 passed in 5.99s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c10_dockerhub_publish_gate.py` passed: `7 passed in 0.08s`.
- `python -m pytest -q tests\test_v8_c4_ci_workflow.py tests\test_v8_c5_ci_docker_build.py tests\test_v8_c6_image_versioning.py tests\test_v8_c8_dockerhub_publishing_plan.py tests\test_v8_c9_dockerhub_secrets_setup.py tests\test_v8_c10_dockerhub_publish_gate.py` passed: `37 passed in 0.26s`.
- `python -m pytest -q` passed: `358 passed in 5.68s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c9_dockerhub_secrets_setup.py tests\test_v8_c10_dockerhub_publish_gate.py` passed: `14 passed in 0.11s`.
- `python -m pytest -q` passed: `359 passed in 6.04s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c10_dockerhub_publish_gate.py tests\test_v8_c9_dockerhub_secrets_setup.py` passed: `15 passed in 0.13s`.
- `python -m pytest -q` passed: `360 passed in 5.84s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c11_dockerhub_publish_validation.py` passed: `5 passed in 0.05s`.
- `python -m pytest -q tests\test_v8_c9_dockerhub_secrets_setup.py tests\test_v8_c10_dockerhub_publish_gate.py tests\test_v8_c11_dockerhub_publish_validation.py` passed: `20 passed in 0.13s`.
- `python -m pytest -q` passed: `365 passed in 8.68s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c12_docker_rollback_guide.py` passed: `5 passed in 0.04s`.
- `python -m pytest -q tests\test_v8_c11_dockerhub_publish_validation.py tests\test_v8_c12_docker_rollback_guide.py` passed: `10 passed in 0.06s`.
- `python -m pytest -q` passed: `370 passed in 5.33s`.
- `git diff --check` passed with CRLF normalization warnings only.
- `python -m pytest -q tests\test_v8_c13_cloud_run_deployment_foundation.py` passed: `6 passed in 0.06s`.
- `python -m pytest -q tests\test_v8_c12_docker_rollback_guide.py tests\test_v8_c13_cloud_run_deployment_foundation.py` passed: `11 passed in 0.06s`.
- `python -m pytest -q` passed: `376 passed in 7.35s`.
- `git diff --check` passed with CRLF normalization warnings only.

## Outcome
V8-C1 adds the first reproducible serving image boundary.

The API can now be packaged separately from the local Python virtual environment. Runtime model state remains outside the image by design.

V8-C2 adds a repeatable Docker Compose runtime for local serving with controlled mounts for model registry metadata, MLflow artifacts, and logs.

V8-C3 adds explicit serving runtime configuration for Docker, Compose, and future CI/CD deployment validation.

V8-C4 adds the first GitHub Actions CI test gate.

V8-C5 adds the CI Docker image build gate after the test gate.

V8-C6 adds the Docker image versioning contract and traceable CI image tags.

V8-C7 documents how to run and interpret the manual CI workflow.

V8-C8 documents Docker Hub publishing requirements while keeping CI free of registry login and push steps.

V8-C9 documents Docker Hub secret setup while keeping CI free of registry login and push steps.

V8-C10 adds manually gated Docker Hub publishing while keeping normal validation runs non-publishing by default.

V8-C11 records successful Docker Hub publish validation and clarifies that live Cloud Run deployment remains out of V8 scope.

V8-C12 documents Docker image rollback using exact Git SHA image tags and keeps Cloud Run rollback for a later live deployment chunk.

V8-C13 documents the manual Cloud Run deployment foundation and keeps GitHub Actions GCP deployment automation for a later chunk.
