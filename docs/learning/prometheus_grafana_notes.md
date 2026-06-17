# Prometheus And Grafana Notes

These notes explain Prometheus and Grafana from the beginning and connect each concept to how ModelOpsLab uses them in V9.

## Big Picture

Prometheus and Grafana are monitoring tools.

The simple mental model is:

```text
application exposes metrics
-> Prometheus collects and stores metrics
-> Grafana visualizes metrics in dashboards
```

In ModelOpsLab:

```text
FastAPI /metrics
-> Prometheus scrape job
-> Grafana datasource
-> ModelOpsLab Monitoring dashboard
```

## What Is A Metric?

A metric is a numeric measurement over time.

Examples:

```text
request count
failure rate
p95 latency
active alert count
drifted feature count
```

Metrics are different from logs.

Logs answer:

```text
What happened in one event?
```

Metrics answer:

```text
How is the system behaving over time?
```

In ModelOpsLab, prediction events are stored in:

```text
logs/predictions.jsonl
```

Those logs are summarized into reports, and the reports are exposed as metrics through:

```text
GET /metrics
```

## What Is Prometheus?

Prometheus is a metrics collection and query system.

Its main job is:

```text
regularly collect metrics from applications
store those metric values over time
let users query those values
```

Prometheus does not usually receive metrics pushed into it.

Instead, it pulls metrics from applications. This is called scraping.

## What Is Scraping?

Scraping means:

```text
Prometheus sends an HTTP request to a metrics endpoint at a fixed interval
the application returns metrics text
Prometheus stores those values with a timestamp
```

In our project, Prometheus scrapes:

```text
host.docker.internal:8000/metrics
```

The Prometheus scrape configuration is stored in:

```text
deployment/monitoring/prometheus/prometheus.yml
```

Why not `localhost:8000` inside Prometheus?

Because Prometheus runs inside a Docker container. Inside that container, `localhost` means the Prometheus container itself, not your Windows host machine.

Docker Desktop gives containers a special host name:

```text
host.docker.internal
```

That lets Prometheus reach the FastAPI app running on your machine.

## What Is The `/metrics` Endpoint?

`/metrics` is an HTTP endpoint that returns metrics in Prometheus text format.

In ModelOpsLab:

```text
http://127.0.0.1:8000/metrics
```

The implementation is in:

```text
app/observability/prometheus_metrics.py
app/api/routes.py
```

The route is:

```text
GET /metrics
```

We used:

```text
prometheus-client
```

Why this matters:

```text
prometheus-client creates Prometheus-compatible metric output
we avoid hand-writing metric text manually
Grafana can query these metrics through Prometheus
```

## Metrics We Expose In ModelOpsLab

The `/metrics` endpoint exposes local V9 monitoring signals such as:

```text
modelopslab_prediction_requests
modelopslab_prediction_successes
modelopslab_prediction_failures
modelopslab_prediction_failure_rate
modelopslab_prediction_latency_ms
modelopslab_telemetry_events
modelopslab_monitoring_active_alerts
modelopslab_monitoring_status
modelopslab_data_drift_detected
modelopslab_data_drifted_features
modelopslab_data_drift_inference_rows
modelopslab_monitoring_report_available
```

These metrics come from local report files:

```text
reports/monitoring/prediction_summary.json
reports/monitoring/alerts.json
reports/drift/data_drift_summary.json
```

Important idea:

```text
Prometheus does not calculate our ML monitoring logic.
ModelOpsLab calculates the monitoring reports.
Prometheus collects the final numeric signals.
```

## What Is Grafana?

Grafana is a dashboard and visualization tool.

Its main job is:

```text
connect to a data source
run metric queries
display the results as panels
```

Grafana does not scrape the FastAPI app directly in our setup.

Instead:

```text
Grafana queries Prometheus
Prometheus scrapes FastAPI
FastAPI exposes /metrics
```

This separation is important.

Prometheus is the metric store.

Grafana is the visual layer.

## What Is A Datasource?

A Grafana datasource tells Grafana where to query data.

In our project, the datasource is:

```text
ModelOpsLab Prometheus
```

It points to:

```text
http://prometheus:9090
```

The file is:

```text
deployment/monitoring/grafana/provisioning/datasources/prometheus.yaml
```

Why `http://prometheus:9090`?

Because Grafana and Prometheus run in the same Docker Compose network. The service name `prometheus` becomes the hostname.

## What Is A Dashboard?

A Grafana dashboard is a collection of panels.

A panel is one chart, stat, table, or visualization.

In ModelOpsLab, the dashboard file is:

```text
deployment/monitoring/grafana/dashboards/modelopslab-monitoring.json
```

The dashboard includes panels for:

```text
prediction requests
failure rate
p95 latency
active alerts
latency metrics
telemetry quality
data drift detected
drifted feature count
report availability
```

## What Is Provisioning?

Provisioning means configuring Grafana from files instead of clicking everything manually in the UI.

In our project, provisioning files are:

```text
deployment/monitoring/grafana/provisioning/datasources/prometheus.yaml
deployment/monitoring/grafana/provisioning/dashboards/modelopslab.yaml
```

Why this is useful:

```text
the dashboard setup is reproducible
the project documents exactly how Grafana is configured
the setup can be committed to Git
another machine can recreate the same dashboard
```

You can still learn from the Grafana UI, but the base setup is stored as code.

## Our Local Stack

The local stack file is:

```text
deployment/docker-compose.monitoring.yaml
```

It starts:

```text
Prometheus on http://localhost:9090
Grafana on http://localhost:3000
```

Command:

```powershell
docker compose -f deployment/docker-compose.monitoring.yaml up
```

Before running it, the FastAPI app should be running:

```powershell
uvicorn app.serve_api:app --reload
```

## What To Check In The UI

### FastAPI

Open:

```text
http://127.0.0.1:8000/metrics
```

You should see text metrics.

### Prometheus

Open:

```text
http://localhost:9090
```

Check:

```text
Status -> Target health
```

Expected:

```text
modelopslab-serving UP
```

Try a query:

```text
modelopslab_prediction_requests
```

### Grafana

Open:

```text
http://localhost:3000
```

Login:

```text
username: admin
password: admin
```

Open:

```text
Dashboards -> ModelOpsLab -> ModelOpsLab Monitoring
```

## How To Debug Common Problems

### `/metrics` Does Not Load

Check:

```text
Is FastAPI running?
Is it running on port 8000?
Did the app import without errors?
```

### Prometheus Target Is DOWN

Check:

```text
Can you open http://127.0.0.1:8000/metrics from the host?
Is Docker Desktop running?
Is Prometheus using host.docker.internal:8000?
Is Windows firewall blocking the connection?
```

### Grafana Dashboard Is Empty

Check:

```text
Is Prometheus target UP?
Does Prometheus query modelopslab_prediction_requests return data?
Is the Grafana datasource pointing to http://prometheus:9090?
Is the dashboard time range too narrow?
```

### Metrics Show Zero

This can happen when local report files are missing or stale.

Regenerate reports:

```powershell
python -m app.build_prediction_monitoring_summary
python -m app.build_monitoring_alerts
python -m app.build_inference_snapshot
python -m app.build_data_drift_summary
python -m app.build_dashboard_snapshot
```

Then refresh Prometheus and Grafana.

## Important Learning Difference

ModelOpsLab has three dashboard layers now:

```text
local JSON reports
local static HTML dashboard
Grafana dashboard
```

They serve different purposes.

### Local JSON Reports

Best for:

```text
tests
automation
debugging exact values
pipeline inputs
```

### Local HTML Dashboard

Best for:

```text
quick local viewing
no external services
simple visual validation
```

### Grafana Dashboard

Best for:

```text
production-style monitoring
time-series visualization
team dashboards
Prometheus-backed observability
```

## Mental Model

Think of the complete V9 monitoring path like this:

```text
prediction request
-> prediction telemetry log
-> monitoring summary
-> alerts and drift reports
-> /metrics endpoint
-> Prometheus scrape
-> Grafana dashboard
```

Each tool has one job:

```text
ModelOpsLab creates ML monitoring signals
Prometheus stores metrics over time
Grafana shows those metrics visually
```
