# V8 Commit Log

## Pending - v8-c1: add Docker serving image foundation

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
