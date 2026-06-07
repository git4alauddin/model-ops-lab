# V7 Serving Flow

This diagram shows the current V7 model serving flow.

It is intentionally limited to implemented V7 behavior: FastAPI health/readiness endpoints, single prediction, batch prediction, schema validation, local registry-based model loading, prediction service execution, prediction audit logging, and serving runtime logging.

```mermaid
flowchart TD
    client["Client / Swagger / terminal"]
    api["FastAPI app<br/>app.serve_api:app"]

    health["GET /health"]
    health_response["status=ok<br/>service + api_version"]

    ready["GET /ready"]
    readiness["app.serving.readiness<br/>find one champion"]
    registry["model_registry/*.json<br/>local champion metadata"]
    ready_response["ready response<br/>model_loaded=true"]
    not_ready_response["not_ready response<br/>HTTP 503"]

    predict["POST /predict"]
    batch["POST /predict/batch"]

    single_schema["PredictionRequest<br/>schema v1 validation"]
    batch_schema["BatchPredictionRequest<br/>non-empty instances"]

    loader["app.serving.model_loader<br/>load_champion_model"]
    mlflow_artifact["mlruns/<experiment>/<run>/artifacts/model.pkl"]
    loaded_model["LoadedModel<br/>model + metadata + artifact_path"]

    predictor["app.serving.predictor<br/>predict_customer_churn"]
    single_response["PredictionResponse<br/>prediction + probability<br/>model_version + request_id"]
    batch_response["BatchPredictionResponse<br/>request_id + predictions"]

    prediction_audit["logs/predictions.jsonl<br/>structured prediction events"]
    runtime_log["logs/modelopslab.log<br/>human-readable serving timeline"]

    error_response["Serving error response<br/>HTTP 503 or HTTP 500"]

    client --> api

    api --> health
    health --> health_response

    api --> ready
    ready --> readiness
    readiness --> registry
    registry -- exactly one champion --> ready_response
    registry -- missing or ambiguous --> not_ready_response

    api --> predict
    predict --> single_schema
    single_schema --> loader

    api --> batch
    batch --> batch_schema
    batch_schema --> loader

    loader --> registry
    loader --> mlflow_artifact
    mlflow_artifact --> loaded_model

    loaded_model --> predictor
    single_schema --> predictor
    batch_schema --> predictor

    predictor --> single_response
    predictor --> batch_response

    single_response --> prediction_audit
    batch_response --> prediction_audit
    single_response --> runtime_log
    batch_response --> runtime_log

    loader -- model unavailable --> error_response
    predictor -- prediction failure --> error_response
    error_response --> prediction_audit
    error_response --> runtime_log
```

## Operational Meaning

V7 turns the locally managed champion model into an HTTP-serving surface.

The API exposes health and readiness separately. Health only proves the FastAPI service is alive. Readiness checks local registry state and reports ready only when one champion model is available. Prediction requests are validated with Pydantic before model loading or prediction execution.

Single and batch prediction use the same model loading and prediction service foundations. The serving layer loads the champion model from local registry metadata, resolves the local MLflow artifact path, runs prediction, and returns model version plus request ID in the response.

Serving observability has two log outputs:

```text
logs/modelopslab.log
  human-readable runtime timeline

logs/predictions.jsonl
  structured prediction audit events
```

## Current Boundary

V7 serving is local FastAPI serving.

The API is started with:

```powershell
uvicorn app.serve_api:app --reload
```

Generated runtime files are ignored by git:

```text
logs/
mlruns/
model_registry/*.json
artifacts/
```
