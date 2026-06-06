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
