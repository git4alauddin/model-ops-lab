# Grafana And Prometheus Local Stack

## Purpose
This guide connects the V9 `/metrics` endpoint to Prometheus and Grafana for local learning.

It uses:

```text
FastAPI /metrics
-> Prometheus scrape target
-> Grafana Prometheus datasource
-> ModelOpsLab dashboard
```

## Files

```text
deployment/docker-compose.monitoring.yaml
deployment/monitoring/prometheus/prometheus.yml
deployment/monitoring/grafana/provisioning/datasources/prometheus.yaml
deployment/monitoring/grafana/provisioning/dashboards/modelopslab.yaml
deployment/monitoring/grafana/dashboards/modelopslab-monitoring.json
```

## Start The Serving API First
Prometheus scrapes the local FastAPI API on port `8000`.

Start the API:

```powershell
uvicorn app.serve_api:app --reload
```

Check:

```text
http://127.0.0.1:8000/metrics
```

## Start Prometheus And Grafana
From the project root:

```powershell
docker compose -f deployment/docker-compose.monitoring.yaml up
```

Open Prometheus:

```text
http://localhost:9090
```

Open Grafana:

```text
http://localhost:3000
```

Default local login:

```text
username: admin
password: admin
```

## What Prometheus Scrapes
Prometheus scrapes:

```text
host.docker.internal:8000/metrics
```

This target works with Docker Desktop on Windows because the container needs to reach the API running on the host machine.

## Grafana Dashboard
Grafana is provisioned with:

```text
datasource: ModelOpsLab Prometheus
dashboard: ModelOpsLab Monitoring
```

The dashboard includes:

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

## Important Boundary
This stack is local monitoring infrastructure.

It does not send alerts, persist long-term Prometheus storage, deploy to Cloud Run, or configure managed cloud monitoring.
