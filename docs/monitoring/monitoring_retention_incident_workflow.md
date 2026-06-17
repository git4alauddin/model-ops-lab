# Monitoring Retention And Incident Debugging Workflow

## Purpose
This document explains how ModelOpsLab should retain local monitoring artifacts and how to reconstruct a production-style incident during V9.

V9 monitoring has two jobs:

```text
show current system health
preserve enough evidence to debug what happened later
```

## Monitoring Artifacts

### Prediction Telemetry Log

```text
logs/predictions.jsonl
```

Purpose:

```text
raw prediction event history
request IDs
model version
deployment version
success and failure events
latency
prediction and probability
validated input feature snapshots when available
```

This is the lowest-level local observability source.

### Prediction Monitoring Summary

```text
reports/monitoring/prediction_summary.json
```

Purpose:

```text
request count
success count
failure count
failure rate
latency statistics
prediction distribution
probability distribution
telemetry filtering quality
```

This report converts raw prediction telemetry into operational signals.

### Monitoring Alerts

```text
reports/monitoring/alerts.json
```

Purpose:

```text
missing telemetry alerts
high failure rate alerts
high p95 latency alerts
prediction distribution collapse alerts
data drift alerts
recommended actions
```

This report answers:

```text
Which monitoring signals need attention?
```

### Drift Reports

```text
reports/drift/reference_baseline.json
reports/drift/inference_snapshot.json
reports/drift/data_drift_summary.json
```

Purpose:

```text
training-data reference distribution
current inference feature distribution
baseline-vs-inference drift comparison
drifted feature list
insufficient data status
```

These reports answer:

```text
Are production inputs still similar to training inputs?
```

### Dashboard Snapshot

```text
reports/monitoring/dashboard_snapshot.json
```

Purpose:

```text
dashboard-ready combined monitoring state
request card
latency card
alert card
drift card
telemetry quality card
report freshness
source report paths
```

This file is the bridge between raw reports and dashboards.

### Local HTML Dashboard

```text
reports/monitoring/dashboard.html
```

Purpose:

```text
quick local visual inspection
no server required
no Grafana required
```

### Prometheus Metrics Endpoint

```text
GET /metrics
```

Purpose:

```text
Prometheus-compatible numeric monitoring signals
Grafana data source through Prometheus
report availability metrics
```

### Prometheus And Grafana

```text
Prometheus: http://localhost:9090
Grafana: http://localhost:3000
```

Purpose:

```text
time-series monitoring
dashboard panels
visual operational debugging
```

## Git Retention Boundary

Local monitoring artifacts are intentionally ignored by Git:

```text
logs/
reports/
```

Reason:

```text
they are runtime evidence
they can change frequently
they may contain environment-specific behavior
they may include sensitive or privacy-sensitive telemetry
```

The code, docs, tests, and configuration that generate or visualize those artifacts are committed.

Examples:

```text
app/observability/
app/build_*.py
deployment/monitoring/
docs/monitoring/
tests/
```

## Local Retention Recommendation

For local learning, keep recent monitoring artifacts while actively debugging.

Recommended local retention:

```text
keep current logs/predictions.jsonl during V9 experiments
regenerate reports after important telemetry changes
keep dashboard screenshots only when needed for portfolio evidence
do not commit runtime reports or logs
do not store secrets in monitoring files
```

Before a major workflow reset, either archive important local evidence outside Git or intentionally regenerate reports from fresh traffic.

## Privacy Boundary

Prediction telemetry should be useful for debugging without becoming an unsafe data dump.

V9 keeps:

```text
validated feature values needed for drift checks
prediction outputs
model and deployment metadata
error category and message
```

V9 avoids:

```text
raw invalid request payloads
secrets
credentials
large unbounded request bodies
personal identifiers beyond the project schema
```

Validation failure telemetry does not store the invalid raw payload because failed payloads may be malformed or unsafe.

## Incident Debugging Workflow

Use this order when investigating a monitoring problem.

### Step 1: Start With The Symptom

The symptom may appear in:

```text
Grafana dashboard
Prometheus query
reports/monitoring/dashboard.html
reports/monitoring/alerts.json
API response failure
```

Examples:

```text
failure rate is high
p95 latency increased
data drift detected
Prometheus target is down
Grafana panels show no data
prediction distribution collapsed
```

### Step 2: Check Service Health

Check:

```text
GET /health
GET /ready
GET /metrics
```

Expected:

```text
/health returns ok
/metrics returns Prometheus text
/ready returns ready only when a champion model is available
```

If `/metrics` is down, Prometheus and Grafana cannot show current metrics even if local reports exist.

### Step 3: Check Prometheus Target Health

Open:

```text
http://localhost:9090
```

Check:

```text
Status -> Target health
```

Expected target:

```text
modelopslab-serving
host.docker.internal:8000/metrics
UP
```

If the target is down:

```text
confirm FastAPI is running on port 8000
confirm /metrics works in the browser
confirm Docker Desktop is running
confirm prometheus.yml points to host.docker.internal:8000
```

### Step 4: Check Grafana Datasource And Time Range

Open:

```text
http://localhost:3000
```

Check:

```text
datasource: ModelOpsLab Prometheus
dashboard: ModelOpsLab Monitoring
time range: last 30 minutes or wider
```

If panels are empty, query directly in Prometheus:

```text
modelopslab_prediction_requests
modelopslab_monitoring_report_available
modelopslab_data_drift_detected
```

### Step 5: Inspect Alert Report

Open:

```text
reports/monitoring/alerts.json
```

Check:

```text
overall_status
active_alert_count
triggered alert names
metric values
thresholds
recommended actions
```

This explains why the monitoring state is alerting.

### Step 6: Inspect Prediction Summary

Open:

```text
reports/monitoring/prediction_summary.json
```

Check:

```text
request_count
success_count
failure_count
failure_rate
latency_ms
prediction_distribution
probability_distribution
raw_event_count
skipped_event_count
skipped_events
```

If skipped events are high, the telemetry file may include older records from before the V9 telemetry contract.

### Step 7: Inspect Raw Prediction Events

Open:

```text
logs/predictions.jsonl
```

Use request IDs and event fields to inspect:

```text
event_version
event_type
endpoint
status
model_version
deployment_version
error_category
failure_stage
latency_ms
input_features
```

This is where the incident can be traced back to individual prediction events.

### Step 8: Inspect Drift Reports

Open:

```text
reports/drift/data_drift_summary.json
```

Check:

```text
overall_status
drifted_feature_count
insufficient_feature_count
inference_row_count
per-feature status
thresholds
```

If status is:

```text
insufficient_data
```

then generate fresh feature-bearing prediction telemetry and rebuild the drift reports.

### Step 9: Regenerate Monitoring Reports

When local metrics are stale, regenerate in this order:

```powershell
python -m app.build_prediction_monitoring_summary
python -m app.build_monitoring_alerts
python -m app.build_inference_snapshot
python -m app.build_data_drift_summary
python -m app.build_monitoring_alerts
python -m app.build_dashboard_snapshot
python -m app.build_monitoring_dashboard
```

Why `build_monitoring_alerts` appears twice:

```text
first pass refreshes operational alerts
after drift summary is rebuilt, second pass includes latest drift alert state
```

### Step 10: Record The Incident Summary

For a real incident, record:

```text
incident timestamp
symptom
affected endpoint
request IDs when available
model version
deployment version
triggered alerts
drift status
root cause hypothesis
validation command
follow-up action
```

V9 does not yet add a formal incident database. The workflow defines what evidence should be collected.

## Common Incident Patterns

### High Failure Rate

Start with:

```text
reports/monitoring/alerts.json
reports/monitoring/prediction_summary.json
logs/predictions.jsonl
```

Look for:

```text
error_category
failure_stage
model_loading vs prediction vs schema_validation
```

### High Latency

Start with:

```text
modelopslab_prediction_latency_ms
reports/monitoring/prediction_summary.json
logs/modelopslab.log
```

Look for:

```text
p95 latency
p99 latency
model loading behavior
slow prediction events
```

### Data Drift Detected

Start with:

```text
reports/drift/data_drift_summary.json
reports/drift/inference_snapshot.json
reports/drift/reference_baseline.json
```

Look for:

```text
drifted feature names
categorical ratio shifts
numeric mean shifts
range expansion
inference row count
```

### Grafana Empty Dashboard

Start with:

```text
Prometheus target health
modelopslab_monitoring_report_available
Grafana datasource
dashboard time range
```

This is usually a metrics pipeline issue, not an ML model issue.

## V9 Boundary

V9 provides local observability, dashboarding, Prometheus scraping, Grafana visualization, drift checks, and alert-ready reports.

V9 does not provide:

```text
long-term production retention storage
alert notification channels
managed cloud monitoring
real concept drift automation
incident ticketing system
automatic remediation
```

Those are later production maturity topics.
