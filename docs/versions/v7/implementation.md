# V7 Implementation

## V7-C1: Serving API Foundation

### Files Added

```text
app/api/__init__.py
app/api/app.py
app/api/constants.py
app/api/routes.py
app/serve_api.py
tests/test_v7_c1_serving_foundation.py
```

### Files Updated

```text
requirements.txt
docs/versions/v7/
```

### Behavior
- Added a FastAPI application factory.
- Added shared serving constants for service identity and API version.
- Added `GET /health`.
- Added an importable Uvicorn app object at `app.serve_api:app`.
- Added focused tests for app creation and health endpoint behavior.

### Local Run Command

```powershell
uvicorn app.serve_api:app --reload
```

### Health Check

```text
GET /health
```

Expected response:

```json
{
  "status": "ok",
  "service": "modelopslab-serving",
  "api_version": "v7"
}
```

## V7-C2: Readiness Endpoint

### Files Added

```text
app/serving/__init__.py
app/serving/readiness.py
tests/test_v7_c2_readiness_endpoint.py
```

### Files Updated

```text
app/api/routes.py
docs/versions/v7/
```

### Behavior
- Added serving readiness logic.
- Added `GET /ready`.
- Checks the local model registry for exactly one champion model.
- Returns HTTP `200` when a champion model is available.
- Returns HTTP `503` when no champion or multiple champions are found.
- Keeps `/health` independent from `/ready`.

### Readiness Check

```text
GET /ready
```

Ready response:

```json
{
  "status": "ready",
  "service": "modelopslab-serving",
  "model_loaded": true,
  "model_name": "customer_churn_model",
  "model_version": "v1-example",
  "mlflow_run_id": "run-example"
}
```

Not-ready response:

```json
{
  "status": "not_ready",
  "service": "modelopslab-serving",
  "model_loaded": false,
  "reason": "No champion model found."
}
```

## V7-C3: Inference Request And Response Schemas

### Files Added

```text
app/api/schemas.py
tests/test_v7_c3_inference_schemas.py
```

### Files Updated

```text
docs/versions/v7/
```

### Behavior
- Added `PredictionRequest`.
- Added `PredictionResponse`.
- Added `ServingErrorResponse`.
- Enforced inference schema version `v1`.
- Rejected unexpected request fields.
- Rejected invalid numeric ranges.
- Rejected invalid categorical values.

### Prediction Request Shape

```json
{
  "schema_version": "v1",
  "tenure_months": 12,
  "monthly_charges": 79.5,
  "total_charges": 950.0,
  "contract_type": "month_to_month",
  "internet_service": "fiber_optic",
  "payment_method": "credit_card",
  "is_senior": false
}
```

### Prediction Response Shape

```json
{
  "status": "success",
  "prediction": 1,
  "probability": 0.82,
  "model_name": "customer_churn_model",
  "model_version": "v1-ready",
  "request_id": "request-1",
  "latency_ms": 12.4
}
```

### Error Response Shape

```json
{
  "status": "failed",
  "error": "Model unavailable.",
  "request_id": "request-1"
}
```

## V7-C4: Registry-Based Model Loader

### Files Added

```text
app/serving/model_loader.py
tests/test_v7_c4_model_loader.py
```

### Files Updated

```text
docs/versions/v7/
```

### Behavior
- Added `LoadedModel`.
- Added `ModelLoaderError`.
- Added champion metadata resolution for serving.
- Requires exactly one champion model.
- Resolves local model artifact file paths.
- Resolves `mlflow-run://<run_id>/artifacts/model` references to local MLflow artifacts.
- Loads model artifacts with `joblib`.
- Returns model object, registry metadata, and resolved artifact path together.

### Loader Flow

```text
load_champion_model
  -> resolve_champion_model_metadata
  -> resolve_model_artifact_path
  -> joblib.load
  -> LoadedModel(model, metadata, artifact_path)
```

### Failure Behavior

```text
no champion model              -> ModelLoaderError
multiple champion models       -> ModelLoaderError
missing artifact               -> ModelLoaderError
invalid MLflow artifact URI    -> ModelLoaderError
unloadable model artifact      -> ModelLoaderError
```

## V7-C5: Prediction Service

### Files Added

```text
app/serving/predictor.py
tests/test_v7_c5_predictor.py
```

### Files Updated

```text
docs/versions/v7/
```

### Behavior
- Converts `PredictionRequest` into the exact feature dataframe expected by the model.
- Runs `predict()` on the loaded champion model.
- Runs `predict_proba()` when available.
- Falls back to hard-label probability when `predict_proba()` is unavailable.
- Builds `PredictionResponse` with model name, model version, request ID, and latency.
- Raises `PredictionError` for invalid prediction output, invalid probability output, missing request ID, or model failure.

### Prediction Service Flow

```text
predict_customer_churn
  -> build_model_input_frame
  -> model.predict
  -> model.predict_proba if available
  -> PredictionResponse
```

## V7-C6: Prediction Endpoint

### Files Added

```text
tests/test_v7_c6_predict_endpoint.py
```

### Files Updated

```text
app/api/routes.py
docs/versions/v7/
```

### Behavior
- Added `POST /predict`.
- Accepts `PredictionRequest`.
- Loads the active champion model.
- Calls the prediction service.
- Generates a request ID for each prediction request.
- Returns `PredictionResponse` on success.
- Returns HTTP `422` for invalid request payloads through FastAPI/Pydantic validation.
- Returns HTTP `503` when the champion model cannot be loaded.
- Returns HTTP `500` when prediction execution fails.

### Swagger Flow

```text
uvicorn app.serve_api:app --reload
open http://127.0.0.1:8000/docs
expand POST /predict
click Try it out
submit a valid request body
```

## V7-C7: Prediction Logging

### Files Added

```text
app/serving/prediction_logging.py
tests/test_v7_c7_prediction_logging.py
```

### Files Updated

```text
app/api/routes.py
docs/versions/v7/
```

### Behavior
- Added JSONL prediction logging.
- Writes successful prediction records.
- Writes model loading failure records.
- Writes prediction execution failure records.
- Includes timestamp, request ID, status, schema version, model identity, prediction, probability, latency, or error.
- Leaves invalid `422` request payloads unlogged because FastAPI rejects them before route execution.

### Log Path

```text
logs/predictions.jsonl
```

### Success Log Shape

```json
{
  "timestamp": "2026-06-07T00:00:00+00:00",
  "request_id": "request-1",
  "status": "success",
  "model_name": "customer_churn_model",
  "model_version": "v1-test",
  "schema_version": "v1",
  "prediction": 1,
  "probability": 0.82,
  "latency_ms": 4.2
}
```

### Failure Log Shape

```json
{
  "timestamp": "2026-06-07T00:00:00+00:00",
  "request_id": "request-1",
  "status": "failed",
  "schema_version": "v1",
  "error": "No champion model found."
}
```

## V7-C8: Batch Prediction Endpoint

### Files Added

```text
tests/test_v7_c8_batch_prediction_endpoint.py
```

### Files Updated

```text
app/api/schemas.py
app/api/routes.py
docs/versions/v7/
```

### Behavior
- Added `BatchPredictionRequest`.
- Added `BatchPredictionResponse`.
- Added `POST /predict/batch`.
- Validates a non-empty `instances` list.
- Loads the champion model once per batch request.
- Runs prediction service once per instance.
- Logs each successful prediction result.
- Returns HTTP `422` for empty batch or invalid instance payloads.
- Returns HTTP `503` when the champion model cannot be loaded.
- Returns HTTP `500` when prediction execution fails.

### Batch Request Shape

```json
{
  "instances": [
    {
      "schema_version": "v1",
      "tenure_months": 12,
      "monthly_charges": 79.5,
      "total_charges": 950.0,
      "contract_type": "month_to_month",
      "internet_service": "fiber_optic",
      "payment_method": "credit_card",
      "is_senior": false
    }
  ]
}
```

## V7-C9: Serving Runtime Logging

### Files Added

```text
app/serving/runtime_logging.py
tests/test_v7_c9_serving_runtime_logging.py
```

### Files Updated

```text
app/api/routes.py
docs/versions/v7/
```

### Behavior
- Added human-readable serving runtime logging.
- Logs prediction request receipt.
- Logs successful prediction request completion.
- Logs controlled model loading failures.
- Logs controlled prediction failures.
- Writes serving runtime events to `logs/modelopslab.log`.
- Keeps detailed prediction audit records in `logs/predictions.jsonl`.

### Runtime Log Shape

```text
Prediction request received. endpoint=/predict request_id=<id> instances=1
Prediction request completed. endpoint=/predict request_id=<id> model_name=customer_churn_model model_version=<version> predictions=1
Prediction request failed. endpoint=/predict request_id=<id> stage=model_loading error=<error>
```

## V7-C10: Serving Flow Diagram

### Files Added

```text
docs/diagrams/v7_serving_flow.md
```

### Files Updated

```text
docs/versions/v7/
```

### Behavior
- Added a Mermaid diagram for the implemented V7 serving flow.
- Documented `/health`.
- Documented `/ready`.
- Documented `/predict`.
- Documented `/predict/batch`.
- Documented schema validation, registry lookup, model artifact loading, prediction service execution, prediction audit logging, and serving runtime logging.

## V7-C11: Serving Version Closure

### Files Added

```text
tests/test_v7_c11_serving_closure.py
```

### Files Updated

```text
docs/versions/v7/
```

### Behavior
- Added closure checks for the implemented V7 serving routes.
- Added closure checks for inference schema availability.
- Added closure checks for serving module files.
- Added closure checks for V7 documentation and serving diagram files.
- Marked V7 complete in the overview.
- Confirmed V7 stops at local FastAPI serving before V8 Docker packaging.
