# V9 Observability Flow

This diagram shows the final V9 monitoring, drift detection, and production observability foundation.

It is intentionally limited to implemented V9 behavior: prediction telemetry, local monitoring reports, alert rules, drift comparison, dashboard snapshot, static dashboard, Prometheus `/metrics`, Prometheus scraping, Grafana dashboarding, retention guidance, and incident debugging workflow.

```mermaid
flowchart TD
    client["Client / Swagger / test traffic"]

    subgraph serving_api["Serving API telemetry"]
        api["FastAPI serving API"]
        predict["/predict and /predict/batch"]
        validation_failure["validation failure telemetry"]
        prediction_success["prediction success telemetry"]
        prediction_failure["prediction failure telemetry"]
        prediction_log["logs/predictions.jsonl<br/>V9 telemetry events"]
    end

    subgraph monitoring_reports["Monitoring reports"]
        monitoring_summary_cmd["python -m app.build_prediction_monitoring_summary"]
        monitoring_summary["reports/monitoring/prediction_summary.json"]
        alerts_cmd["python -m app.build_monitoring_alerts"]
        alerts["reports/monitoring/alerts.json"]
    end

    subgraph drift_detection["Drift detection"]
        baseline_cmd["python -m app.build_drift_reference_baseline"]
        baseline["reports/drift/reference_baseline.json"]
        inference_cmd["python -m app.build_inference_snapshot"]
        inference_snapshot["reports/drift/inference_snapshot.json"]
        drift_cmd["python -m app.build_data_drift_summary"]
        drift_summary["reports/drift/data_drift_summary.json"]
    end

    subgraph dashboard_artifacts["Dashboard artifacts"]
        dashboard_snapshot_cmd["python -m app.build_dashboard_snapshot"]
        dashboard_snapshot["reports/monitoring/dashboard_snapshot.json"]
        html_dashboard_cmd["python -m app.build_monitoring_dashboard"]
        html_dashboard["reports/monitoring/dashboard.html"]
    end

    subgraph prometheus_grafana["Prometheus and Grafana"]
        metrics_endpoint["GET /metrics<br/>prometheus-client"]
        prometheus["Prometheus<br/>scrapes host.docker.internal:8000/metrics"]
        grafana["Grafana<br/>ModelOpsLab Monitoring dashboard"]
    end

    subgraph operations_workflow["Retention and closure"]
        retention_doc["monitoring retention<br/>incident debugging workflow"]
        closure["V9 closure<br/>scope + deferred boundary"]
    end

    client --> api
    api --> predict
    predict --> prediction_success
    predict --> prediction_failure
    api --> validation_failure

    validation_failure --> prediction_log
    prediction_success --> prediction_log
    prediction_failure --> prediction_log

    prediction_log --> monitoring_summary_cmd
    monitoring_summary_cmd --> monitoring_summary
    monitoring_summary --> alerts_cmd

    prediction_log --> inference_cmd
    inference_cmd --> inference_snapshot
    baseline_cmd --> baseline
    baseline --> drift_cmd
    inference_snapshot --> drift_cmd
    drift_cmd --> drift_summary
    drift_summary --> alerts_cmd

    alerts_cmd --> alerts

    monitoring_summary --> dashboard_snapshot_cmd
    alerts --> dashboard_snapshot_cmd
    baseline --> dashboard_snapshot_cmd
    inference_snapshot --> dashboard_snapshot_cmd
    drift_summary --> dashboard_snapshot_cmd
    dashboard_snapshot_cmd --> dashboard_snapshot
    dashboard_snapshot --> html_dashboard_cmd
    html_dashboard_cmd --> html_dashboard

    monitoring_summary --> metrics_endpoint
    alerts --> metrics_endpoint
    drift_summary --> metrics_endpoint
    metrics_endpoint --> prometheus
    prometheus --> grafana

    html_dashboard --> retention_doc
    grafana --> retention_doc
    prediction_log --> retention_doc
    monitoring_summary --> retention_doc
    alerts --> retention_doc
    drift_summary --> retention_doc
    retention_doc --> closure
```

## Operational Meaning

V9 turns the serving system into an observable ML service.

Prediction requests produce structured telemetry events. Local commands convert those events into monitoring summaries, alert reports, drift baselines, inference snapshots, and data drift summaries. The dashboard snapshot combines those report outputs into one dashboard-ready contract, then the local HTML dashboard renders a no-service visual view.

The Prometheus path exposes the same local monitoring signals through:

```text
GET /metrics
```

Prometheus scrapes the endpoint and Grafana visualizes the time-series metrics through the provisioned `ModelOpsLab Monitoring` dashboard.

The incident debugging workflow ties the visual layer back to the source evidence:

```text
Grafana symptom
-> Prometheus metric
-> local monitoring report
-> raw prediction telemetry
```

## Current Boundary

V9 is closed as the local-first observability foundation.

It includes:

```text
prediction telemetry
local monitoring reports
alert-ready metrics
data drift comparison
dashboard artifacts
Prometheus metrics endpoint
Grafana local stack
retention and incident workflow
```

It intentionally defers:

```text
real concept drift automation
alert notification channels
long-term Prometheus storage
managed cloud monitoring
production retention backend
automatic remediation
```
