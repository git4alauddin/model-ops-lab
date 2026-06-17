# Prediction Telemetry Contract

This document defines the V9 JSONL contract for prediction telemetry.

Runtime prediction telemetry is written to:

```text
logs/predictions.jsonl
```

The file is local runtime output and remains ignored by git.

## Purpose
Prediction telemetry makes each serving request traceable for:

```text
debugging
drift detection
latency monitoring
error monitoring
prediction distribution monitoring
incident reconstruction
```

## Event Format
Each line is one JSON object.

Stable fields:

| Field | Meaning |
|---|---|
| `event_version` | telemetry contract version |
| `event_type` | success, failure, or validation failure event |
| `timestamp` | UTC event timestamp |
| `request_id` | request correlation ID |
| `endpoint` | serving endpoint |
| `status` | `success` or `failed` |
| `input_schema_version` | inference input schema version when available |
| `input_features` | privacy-aware validated feature snapshot when available |
| `model_name` | model name when available |
| `model_version` | model version when available |
| `serving_environment` | local, staging, production, or similar runtime name |
| `deployment_version` | deployed revision, image tag, Git SHA, or local |
| `prediction` | model prediction when available |
| `probability` | model probability when available |
| `latency_ms` | prediction latency when available |
| `error_category` | failure category when available |
| `error_message` | controlled failure message when available |
| `failure_stage` | stage where failure occurred when available |

## Event Types
V9-C2 defines three event types:

```text
prediction_success
prediction_failure
prediction_validation_failure
```

## Success Event
Example:

```json
{
  "event_version": "v1",
  "event_type": "prediction_success",
  "timestamp": "2026-06-17T00:00:00+00:00",
  "request_id": "request-1",
  "endpoint": "/predict",
  "status": "success",
  "input_schema_version": "v1",
  "input_features": {
    "tenure_months": 12,
    "monthly_charges": 79.5,
    "total_charges": 950.0,
    "contract_type": "month_to_month",
    "internet_service": "fiber_optic",
    "payment_method": "credit_card",
    "is_senior": false
  },
  "model_name": "customer_churn_model",
  "model_version": "v1-test",
  "serving_environment": "local",
  "deployment_version": "local",
  "prediction": 1,
  "probability": 0.82,
  "latency_ms": 4.2,
  "error_category": null,
  "error_message": null,
  "failure_stage": null
}
```

## Failure Event
Controlled serving failures use:

```text
prediction_failure
```

Examples:

```text
model_loading
prediction
```

The event keeps model fields empty when the model could not be loaded.

It still keeps `input_features` when the request passed validation, because these features are needed for drift snapshots.

## Validation Failure Event
Schema validation failures use:

```text
prediction_validation_failure
```

These events are logged for invalid `/predict` and `/predict/batch` requests.

The API still returns the normal FastAPI `422` validation response.

Validation failure events keep `input_features` as `null` because the request did not pass the schema contract.

## Feature Snapshot Boundary
`input_features` contains only the validated serving features from `PredictionRequest`.

It excludes:

```text
customer identifiers
target labels
raw invalid payloads
```

The current feature set is:

```text
tenure_months
monthly_charges
total_charges
contract_type
internet_service
payment_method
is_senior
```

## Deployment Version
`DEPLOYMENT_VERSION` identifies the running deployment.

Local default:

```text
local
```

Cloud examples:

```text
Git SHA
Cloud Run revision
container image tag
```

This field links prediction behavior to the deployed artifact that served the request.

## V9-C2 Boundary
V9-C2 defines and wires the telemetry event contract.

It does not add Prometheus metrics, Grafana dashboards, Evidently drift reports, or alert rules.
