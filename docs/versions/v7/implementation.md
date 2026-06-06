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
