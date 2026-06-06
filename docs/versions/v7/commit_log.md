# V7 Commit Log

## Pending - v7-c1: add serving API foundation

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
