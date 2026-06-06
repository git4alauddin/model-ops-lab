# V7 Issues Faced

## Open
No open V7 issues.

## V7-C1: Serving API Foundation

### Issue
The serving layer needed a minimal API foundation before model loading or prediction logic could be added.

### Resolution
Added a FastAPI app factory, shared constants, health route, Uvicorn entry point, focused tests, and version docs.

## V7-C2: Readiness Endpoint

### Issue
FastAPI could not infer a valid response model from a route annotated as `dict | JSONResponse`.

### Resolution
Disabled response-model inference for `/ready` and let the route return either a normal dictionary or a `JSONResponse` with HTTP `503`.

## V7-C3: Inference Schemas

### Issue
Prediction behavior needs a strict input and output contract before `/predict` is implemented.

### Resolution
Added Pydantic schemas for prediction requests, successful prediction responses, and structured serving errors.

## V7-C4: Registry-Based Model Loader

### Issue
Registry records can point to MLflow-style artifact references, while local artifacts are stored as concrete files.

### Resolution
Added artifact URI resolution that maps `mlflow-run://<run_id>/artifacts/model` to the local MLflow `model.pkl` artifact when available.

## V7-C5: Prediction Service

### Issue
Prediction behavior needed to be implemented without coupling it directly to the HTTP route.

### Resolution
Added a pure serving predictor that accepts a validated request and a loaded model, then returns a structured prediction response.

## V7-C6: Prediction Endpoint

### Issue
The prediction endpoint needed to expose model serving without duplicating loader or predictor logic inside the route.

### Resolution
Added a thin FastAPI route that delegates to the model loader and prediction service, then maps controlled failures to HTTP responses.

## V7-C7: Prediction Logging

### Issue
Prediction responses were returned to clients but not persisted for later debugging or monitoring.

### Resolution
Added JSONL prediction logs for successful predictions and controlled serving failures.

## V7-C8: Batch Prediction Endpoint

### Issue
Batch prediction needed to reuse single prediction behavior without loading the model for every instance.

### Resolution
Added a batch route that loads the champion once, runs the existing prediction service for each instance, and logs each successful prediction event.

## V7-C9: Serving Runtime Logging

### Issue
Prediction audit logs existed in `predictions.jsonl`, but the master runtime log did not show serving activity.

### Resolution
Added serving runtime logging to `logs/modelopslab.log` for request receipt, completion, and controlled failures.
