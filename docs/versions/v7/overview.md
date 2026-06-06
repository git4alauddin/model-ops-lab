# V7 Overview

## Version Goal
Add model serving API and inference infrastructure.

V7 moves the project from managed model lifecycle records to an API layer that can serve predictions from the selected model.

## Completion Status
V7 is in progress.

Implemented chunks:
- V7-C1: serving API foundation.
- V7-C2: readiness endpoint.
- V7-C3: inference request and response schemas.
- V7-C4: registry-based model loader.
- V7-C5: prediction service.
- V7-C6: prediction endpoint.
- V7-C7: prediction logging.

## Components To Introduce
- FastAPI application boundary
- health endpoint
- readiness endpoint
- prediction request schema
- prediction response schema
- registry-based model loading
- single prediction endpoint
- batch prediction endpoint
- request ID handling
- prediction logging
- latency tracking
- structured serving errors
- serving flow diagram
- serving documentation

## Serving Direction
V7 starts with a minimal API foundation first.

The first serving boundary proves the service can start and expose operational endpoints before adding model loading and prediction behavior.

## Initial API Surface

```text
GET /health
GET /ready
```

Meaning:

```text
the API process is alive and responding
```

Health does not mean the model is ready. Readiness and prediction behavior will be added separately.

Readiness means:

```text
the API can find exactly one champion model in the local registry
```

If no champion exists or multiple champions exist, `/ready` returns `503` with a `not_ready` response.

## Inference Contract
The first prediction contract is schema version `v1`.

Request fields:

```text
schema_version
tenure_months
monthly_charges
total_charges
contract_type
internet_service
payment_method
is_senior
```

The schema rejects:

```text
missing required fields
unexpected fields
invalid numeric ranges
invalid categorical values
unsupported schema versions
```

## Model Loading Direction
V7 loads the active serving model from the local model registry.

Loader flow:

```text
local registry
-> exactly one champion model
-> artifact URI
-> local model artifact path
-> loaded model object
```

The loader currently supports:

```text
local model artifact file paths
mlflow-run://<run_id>/artifacts/model references
```

## Prediction Direction
Prediction execution is separated from HTTP routing.

Prediction flow:

```text
PredictionRequest
-> exact model input dataframe
-> loaded champion model
-> prediction
-> probability
-> PredictionResponse
```

This keeps core inference behavior testable before wiring it into `POST /predict`.

## Prediction API
`POST /predict` exposes the prediction service through FastAPI.

Endpoint flow:

```text
POST /predict
-> validate PredictionRequest
-> load champion model
-> run prediction service
-> return PredictionResponse
```

Failure behavior:

```text
invalid request payload -> HTTP 422
model unavailable       -> HTTP 503
prediction failure      -> HTTP 500
```

## Prediction Logging
Every valid prediction request that reaches route logic writes a JSONL audit record.

Log path:

```text
logs/predictions.jsonl
```

Logged outcomes:

```text
successful prediction
model loading failure
prediction execution failure
```

Invalid request payloads are rejected by FastAPI before route logic runs, so they are not logged by the prediction logger yet.

## Operational Objectives
- expose model behavior through an HTTP API
- separate API routes from prediction logic
- validate inference requests before prediction
- load model versions through registry metadata
- return model version and request metadata with predictions
- make inference failures observable
- prepare for Dockerized serving in V8
