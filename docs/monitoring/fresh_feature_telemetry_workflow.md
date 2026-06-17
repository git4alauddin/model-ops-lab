# Fresh Feature Telemetry Workflow

This workflow refreshes local monitoring and drift reports after `input_features` has been added to prediction telemetry.

## Purpose
V9-C7 added feature snapshots to validated prediction telemetry.

Older local telemetry does not contain `input_features`, so drift reports can show:

```text
overall_status: insufficient_data
inference_row_count: 0
```

Fresh valid prediction requests create feature-bearing telemetry so the inference snapshot and drift comparison can run.

## Option A: Swagger UI
Start the local serving API:

```powershell
uvicorn app.serve_api:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Use `POST /predict` with valid request bodies.

Example:

```json
{
  "schema_version": "v1",
  "tenure_months": 24,
  "monthly_charges": 45.1,
  "total_charges": 1082.4,
  "contract_type": "one_year",
  "internet_service": "dsl",
  "payment_method": "credit_card",
  "is_senior": false
}
```

## Option B: Local Test Client
For a fast local refresh, use a short FastAPI `TestClient` script to send valid `/predict` and `/predict/batch` requests.

This creates the same local prediction telemetry without opening a browser.

## Rebuild Reports
Run these commands after generating fresh prediction traffic:

```powershell
python -m app.build_prediction_monitoring_summary
python -m app.build_inference_snapshot
python -m app.build_data_drift_summary
python -m app.build_monitoring_alerts
```

## Expected Outputs
The refreshed reports are:

```text
reports/monitoring/prediction_summary.json
reports/drift/inference_snapshot.json
reports/drift/data_drift_summary.json
reports/monitoring/alerts.json
```

After fresh feature-bearing telemetry, `reports/drift/inference_snapshot.json` should show:

```text
row_count > 0
feature_event_count > 0
feature_count = 7
```

Then `reports/drift/data_drift_summary.json` should move from:

```text
overall_status: insufficient_data
```

to either:

```text
overall_status: ok
```

or:

```text
overall_status: drift_detected
```

## Current Local Run
After V9-C9 fresh telemetry generation, the local reports showed:

```text
prediction_summary.request_count: 154
prediction_summary.success_count: 18
inference_snapshot.row_count: 16
inference_snapshot.feature_event_count: 16
data_drift_summary.overall_status: drift_detected
data_drift_summary.inference_row_count: 16
data_drift_summary.drifted_feature_count: 5
alerts.overall_status: alerting
alerts.active_alert_count: 2
```

These values are local learning artifacts, not committed runtime state.

## Boundary
This workflow does not install Evidently, start Prometheus, create Grafana dashboards, or deploy anything.

It proves that the local telemetry and drift pipeline can move from missing inference data to populated drift comparison output.
