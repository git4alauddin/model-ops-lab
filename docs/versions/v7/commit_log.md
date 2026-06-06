# V7 Commit Log

## a241aba - v7-c1: add serving API foundation

### What Changed
- Added FastAPI and Uvicorn dependency declarations.
- Added serving API package.
- Added FastAPI app factory.
- Added `GET /health`.
- Added Uvicorn app entry point.
- Added focused serving foundation tests.
- Added V7 documentation scaffold.

### What Problem It Solved
- Establishes the API serving boundary before readiness, model loading, and prediction endpoints are added.

### Verification
- `python -m pytest -q tests\test_v7_c1_serving_foundation.py` passed: `3 passed in 0.40s`.
- `python -c "from app.serve_api import app; print(app.title); print(app.version)"` printed `ModelOpsLab Serving API` and `v7`.
- `python -m pytest -q` passed: `243 passed in 5.09s`.

## Pending - v7-c2: add readiness endpoint

### What Changed
- Added serving readiness helper.
- Added `GET /ready`.
- Checked local registry for exactly one champion model.
- Returned HTTP `200` when ready.
- Returned HTTP `503` when not ready.
- Added focused readiness endpoint tests.
- Updated V7 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Separates API process health from model-serving readiness.
- Prevents the service from reporting ready when no champion model is available.

### Verification
- `python -m pytest -q tests\test_v7_c2_readiness_endpoint.py` passed: `6 passed in 0.59s`.
- `python -m pytest -q tests\test_v7_c1_serving_foundation.py tests\test_v7_c2_readiness_endpoint.py` passed: `9 passed in 0.63s`.
- `python -m pytest -q` passed: `249 passed in 5.61s`.
