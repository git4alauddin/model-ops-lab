# Continuous ML Lifecycle Architecture

## System Objective

ModelOpsLab demonstrates how an ML system can evolve from reproducible training into a governed operational lifecycle.

The implemented architecture connects:

```text
data validation
reproducible training
experiment tracking
model registry
API serving
container deployment
monitoring and drift detection
governed retraining
validated rollback
```

## Architecture Layers

### Training And Reproducibility

```text
configs/training.yaml
data_versions/
schema_versions/
validation gate
scikit-learn training pipeline
MLflow experiment tracking
```

This layer makes model creation traceable to its configuration, dataset version, schema, and metrics.

### Model Lifecycle

```text
model_registry/
candidate
champion
archived
promotion
rollback
```

The local registry is the source used by the FastAPI serving layer to resolve the active champion.

### Serving And Deployment

```text
FastAPI
/health
/ready
/predict
/predict/batch
Docker
GitHub Actions
Artifact Registry
Cloud Run
```

The deployed Cloud Run foundation validates container delivery and `/health`. Full cloud prediction readiness remains limited by local model artifact storage.

### Observability

```text
prediction telemetry
monitoring summaries
alert reports
data drift comparison
Prometheus metrics
Grafana dashboard
incident debugging workflow
```

This layer produces the signals consumed by V10 retraining governance.

### Governed Retraining

```text
trigger decision
retraining run metadata
candidate training
production comparison
regression gates
human approval
promotion record
serving handoff
local champion update
local rollback
```

Each retraining run persists an audit trail under `retraining_runs/<run_id>/`.

## Control Plane And Runtime Plane

The project separates decisions from runtime mutations.

Control-plane records:

```text
trigger decision
comparison report
approval record
promotion record
serving handoff report
```

Runtime mutations:

```text
local model registry champion update
local champion rollback
Cloud Run deployment
Cloud Run traffic migration
```

This separation prevents a metadata decision from being mistaken for a live production change.

## Safety Model

The V10 safety model includes:

```text
validation before training
comparison against current production
explicit regression gates
human approval
recorded rollback target
artifact checks before registry mutation
readiness and prediction checks after mutation
registry snapshot restoration on failed update or rollback
```

## Key Architecture Decisions

### Local Registry Before Managed Registry

The project uses a filesystem-backed model registry to make lifecycle behavior inspectable and testable without managed-service complexity.

Trade-off:

```text
high learning visibility and low cost
vs
limited distributed concurrency and cloud portability
```

### Prefect Before Airflow

Prefect provides task orchestration and failure visibility with lower local operational overhead.

Trade-off:

```text
fast local iteration
vs
less scheduler infrastructure realism than a managed Airflow deployment
```

### Cloud Run Before Kubernetes

Cloud Run proves container deployment, identity federation, immutable image delivery, and revision-based rollback without cluster operations.

Trade-off:

```text
simpler deployment platform
vs
less control over complex serving topology
```

### Human Approval Before Automatic Promotion

The first retraining maturity level keeps model promotion human-in-the-loop.

Trade-off:

```text
safer and auditable production evolution
vs
slower fully automated remediation
```

## Known Boundaries

```text
synthetic small dataset
local filesystem model and report storage
no delayed production labels
no real concept drift automation
no scheduled V10 retraining execution
no automated Cloud Run rollout from retraining artifacts
no fairness or calibration gate implementation
no managed long-term monitoring backend
```

These are explicit extension points, not hidden claims.

