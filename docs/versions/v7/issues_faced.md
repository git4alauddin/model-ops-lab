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
