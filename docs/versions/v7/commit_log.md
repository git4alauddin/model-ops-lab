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

## b05ba69 - v7-c6: add prediction endpoint

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

## 942dcd1 - v7-c7: add prediction logging

### What Changed
- Added JSONL prediction logging helpers.
- Logged successful prediction responses.
- Logged model loading failures.
- Logged prediction execution failures.
- Added focused prediction logging tests.
- Updated V7 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Makes prediction requests traceable after the HTTP response is returned.
- Creates the local observability foundation needed before batch inference and monitoring.

### Verification
- `python -m pytest -q tests\test_v7_c7_prediction_logging.py` passed: `7 passed in 0.89s`.
- `python -m pytest -q tests\test_v7_c6_predict_endpoint.py tests\test_v7_c7_prediction_logging.py` passed: `11 passed in 0.97s`.
- PowerShell-expanded V7 suite command passed: `43 passed in 1.13s`.
- `python -m pytest -q` passed: `283 passed in 5.64s`.

## 853bba4 - v7-c8: add batch prediction endpoint

### What Changed
- Added batch prediction request schema.
- Added batch prediction response schema.
- Added `POST /predict/batch`.
- Loaded the champion model once per batch request.
- Reused the existing prediction service for each instance.
- Logged each successful prediction result.
- Added focused batch prediction endpoint tests.
- Updated V7 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Supports multi-row inference through the serving API.
- Reuses existing single-prediction validation, loading, prediction, and logging foundations.

### Verification
- `python -m pytest -q tests\test_v7_c8_batch_prediction_endpoint.py` passed: `7 passed in 0.86s`.
- `python -m pytest -q tests\test_v7_c6_predict_endpoint.py tests\test_v7_c7_prediction_logging.py tests\test_v7_c8_batch_prediction_endpoint.py` passed: `18 passed in 0.97s`.
- PowerShell-expanded V7 suite command passed: `50 passed in 1.25s`.
- `python -m pytest -q` passed: `290 passed in 5.50s`.

## 87fc58b - v7-c9: add serving runtime logging

### What Changed
- Added serving runtime logging helpers.
- Logged prediction request receipt.
- Logged successful single and batch prediction completion.
- Logged controlled serving failures.
- Routed serving runtime events to `logs/modelopslab.log`.
- Added focused serving runtime logging tests.
- Updated V7 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Makes serving activity visible in the master runtime log.
- Keeps `modelopslab.log` human-readable while `predictions.jsonl` remains the structured prediction audit log.

### Verification
- `python -m pytest -q tests\test_v7_c9_serving_runtime_logging.py` passed: `4 passed in 0.95s`.
- `python -m pytest -q tests\test_v7_c6_predict_endpoint.py tests\test_v7_c7_prediction_logging.py tests\test_v7_c8_batch_prediction_endpoint.py tests\test_v7_c9_serving_runtime_logging.py` passed: `22 passed in 1.17s`.
- PowerShell-expanded V7 suite command passed: `54 passed in 1.73s`.
- `python -m pytest -q` passed: `294 passed in 7.64s`.

## Pending - v7-c10: add serving flow diagram

### What Changed
- Added V7 serving Mermaid diagram.
- Documented health and readiness paths.
- Documented single and batch prediction paths.
- Documented schema validation, registry lookup, model loading, prediction service, prediction audit logs, and runtime logs.
- Updated V7 docs for implementation, verification, and lessons.

### What Problem It Solved
- Makes the V7 serving architecture explainable from one visual reference.
- Clarifies how request flow, model loading, prediction outputs, and logs connect.

### Verification
- `Get-Content docs\diagrams\v7_serving_flow.md` confirmed the V7 serving flow diagram exists.
- `Select-String -Path docs\diagrams\v7_serving_flow.md -Pattern "flowchart TD|POST /predict|POST /predict/batch|logs/predictions.jsonl|logs/modelopslab.log|model_loader"` found the expected implemented serving nodes.

## Pending - v7-c11: close serving API version

### What Changed
- Added V7 serving closure tests.
- Verified serving routes exist.
- Verified inference schema surface exists.
- Verified serving module files exist.
- Verified V7 docs and serving diagram exist.
- Marked V7 complete in the overview.
- Updated V7 docs for implementation, verification, lessons, and issues.

### What Problem It Solved
- Confirms V7 is complete before moving to V8 Docker packaging.
- Prevents the version from being closed with missing routes, schemas, serving modules, docs, or diagram references.

### Verification
- `python -m pytest -q tests\test_v7_c11_serving_closure.py` passed: `5 passed in 0.84s`.
- PowerShell-expanded V7 suite command passed: `59 passed in 1.32s`.
- `python -m pytest -q` passed: `299 passed in 6.18s`.
- `git diff --check` passed with CRLF normalization warnings only.
