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

## 0fc2805 - v7-c2: add readiness endpoint

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

## 36dda0d - v7-c3: add inference schemas

### What Changed
- Added prediction request schema.
- Added prediction response schema.
- Added structured serving error response schema.
- Enforced inference schema version `v1`.
- Rejected unexpected request fields.
- Added focused inference schema tests.
- Updated V7 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Defines the prediction API contract before adding `/predict`.
- Gives future Swagger documentation a strict request and response shape.

### Verification
- `python -m pytest -q tests\test_v7_c3_inference_schemas.py` passed: `8 passed in 0.13s`.
- PowerShell-expanded V7 suite command passed: `17 passed in 0.59s`.
- `python -m pytest -q` passed: `257 passed in 5.30s`.

## d12531a - v7-c4: add registry-based model loader

### What Changed
- Added serving model loader.
- Added loaded model container.
- Added controlled model loader errors.
- Resolved exactly one champion model from registry metadata.
- Resolved local and MLflow-run artifact references.
- Loaded model artifacts with `joblib`.
- Added focused model loader tests.
- Updated V7 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Prepares the serving layer to load the registry champion model before `/predict` is implemented.
- Avoids hardcoded model paths in the future prediction endpoint.

### Verification
- `python -m pytest -q tests\test_v7_c4_model_loader.py` passed: `8 passed in 0.27s`.
- PowerShell-expanded V7 suite command passed: `25 passed in 0.80s`.
- `python -c "from app.serving.model_loader import load_champion_model; loaded = load_champion_model(); print(loaded.metadata['model_version']); print(loaded.artifact_path.name); print(type(loaded.model).__name__)"` printed `v1-7ab8f00a`, `model.pkl`, and `Pipeline`.
- `python -m pytest -q` passed: `265 passed in 5.12s`.

## 1df15fc - v7-c5: add prediction service

### What Changed
- Added pure prediction service logic.
- Converted validated prediction requests into model input dataframes.
- Called `predict()` and `predict_proba()` when available.
- Added hard-label probability fallback for models without `predict_proba()`.
- Added controlled prediction errors.
- Added focused predictor tests.
- Updated V7 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Enables tested inference behavior before exposing `POST /predict`.
- Keeps model prediction behavior separate from FastAPI route behavior.

### Verification
- `python -m pytest -q tests\test_v7_c5_predictor.py` passed: `7 passed in 1.37s`.
- PowerShell-expanded V7 suite command passed: `32 passed in 1.95s`.
- `python -m pytest -q` passed: `272 passed in 7.73s`.

## Pending - v7-c6: add prediction endpoint

### What Changed
- Added `POST /predict`.
- Wired `PredictionRequest` into the model loader and prediction service.
- Generated request IDs for prediction requests.
- Returned structured success responses.
- Mapped model loading failures to HTTP `503`.
- Mapped prediction failures to HTTP `500`.
- Added focused prediction endpoint tests.
- Updated V7 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Makes the serving API usable for single-row prediction.
- Makes Swagger useful for interactive inference testing.

### Verification
- `python -m pytest -q tests\test_v7_c6_predict_endpoint.py` passed: `4 passed in 0.91s`.
- Command-level FastAPI `POST /predict` check returned HTTP `200`, `success`, prediction `1`, and model version `v1-7ab8f00a`.
- PowerShell-expanded V7 suite command passed: `36 passed in 1.19s`.
- `python -m pytest -q` passed: `276 passed in 8.00s`.
