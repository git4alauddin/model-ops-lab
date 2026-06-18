# Portfolio Demo Checklist

## Goal

Demonstrate the system as an operational lifecycle, not a collection of disconnected tools.

## Recommended Demo Order

### 1. Repository Orientation

Show:

```text
README.md
docs/diagrams/
docs/versions/
app/
deployment/
```

Explain the V1-V10 incremental architecture.

### 2. Training And Validation

Show:

```text
configs/training.yaml
schema_versions/customer_churn_v1.yaml
python -m app.validate_data
python -m app.run_training_pipeline
```

Explain why validation blocks downstream training.

### 3. Experiment And Registry Lifecycle

Show:

```text
MLflow UI
champion selection report
model_registry/
registry query command
```

Explain candidate, champion, archived, and rollback states.

### 4. Local Serving

Run:

```powershell
uvicorn app.serve_api:app --reload
```

Demonstrate:

```text
/health
/ready
/predict
/metrics
```

Point out model version in readiness and prediction responses.

### 5. Monitoring

Show:

```text
prediction telemetry
monitoring summary
alerts
data drift summary
Grafana dashboard
```

Explain the incident debugging path from dashboard to raw telemetry.

### 6. Governed Retraining

Walk through:

```text
trigger decision
retraining metadata
candidate artifacts
comparison report
approval record
promotion record
serving handoff report
local serving update report
rollback report
```

Explain why each record exists and which steps mutate serving.

### 7. Deployment

Show:

```text
.github/workflows/ci.yaml
Artifact Registry validation
Cloud Run deployment evidence
Workload Identity Federation notes
```

State the cloud boundary honestly: deployment `/health` is validated, while retraining-driven cloud model rollout is not implemented.

## Evidence To Capture

Useful portfolio screenshots:

```text
MLflow experiment comparison
FastAPI Swagger prediction
local /ready response
Grafana dashboard
GitHub Actions successful workflow
Artifact Registry image
Cloud Run revision and /health
V10 Mermaid diagram
comparison and rollback reports
```

Do not include secrets, tokens, service-account credentials, or private environment values.

## Final Demo Message

```text
The project demonstrates how an ML model is trained, validated, tracked, served, monitored, retrained, promoted, and rolled back through explicit operational controls.
```

