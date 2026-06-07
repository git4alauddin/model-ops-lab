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

## Commands Executed
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py`
- `python -m pytest -q`
- `docker --version`
- `docker build -f deployment/Dockerfile -t modelopslab-serving:v8-c1 .`
- `docker run --rm modelopslab-serving:v8-c1 python -c "from app.serve_api import app; print(app.title); print(app.version)"`
- `git diff --check`

## Expected Output
- Docker serving foundation tests pass.
- Existing test suite remains passing.
- Docker is available locally.
- Docker image builds successfully when Docker Desktop is running.
- Docker build context excludes local runtime-heavy folders.
- Dockerfile can start the FastAPI serving API inside the image.
- Built image can import the FastAPI serving app.

## Actual Output
- `python -m pytest -q tests\test_v8_c1_docker_serving_foundation.py` passed: `5 passed in 0.05s`.
- `python -m pytest -q` passed: `304 passed in 7.00s`.
- `docker --version` printed `Docker version 29.2.1, build a5c7197`.
- `docker build -f deployment/Dockerfile -t modelopslab-serving:v8-c1 .` built successfully.
- `docker run --rm modelopslab-serving:v8-c1 python -c "from app.serve_api import app; print(app.title); print(app.version)"` printed `ModelOpsLab Serving API` and `v7`.
- `git diff --check` passed with CRLF normalization warnings only.

## Outcome
V8-C1 adds the first reproducible serving image boundary.

The API can now be packaged separately from the local Python virtual environment. Runtime model state remains outside the image by design.
