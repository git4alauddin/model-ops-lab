# ModelOpsLab Project Case Study

## Project Positioning

ModelOpsLab is a production-style end-to-end MLOps platform for reproducible ML training, deployment, monitoring, drift detection, governed retraining, and operational lifecycle management.

## Problem

Training a model is only the beginning of an operational ML system.

A production-oriented system must answer:

```text
Can the training run be reproduced?
Can bad data block training?
Can experiments be compared?
Which model is serving?
Can the service be deployed safely?
Can behavior be monitored?
Can drift lead to controlled retraining?
Can a weak candidate be blocked?
Can a serving change be rolled back?
```

ModelOpsLab was built incrementally to answer those questions with explicit artifacts, tests, commands, and documentation.

## Implemented Lifecycle

```text
V1  reproducible baseline training
V2  data validation and quality gates
V3  dataset lineage and reproducibility checks
V4  MLflow experiment tracking and champion selection
V5  Prefect orchestration and pipeline metadata
V6  local model registry, promotion, and rollback
V7  FastAPI serving and prediction telemetry
V8  Docker, GitHub Actions, Artifact Registry, and Cloud Run
V9  monitoring, drift detection, Prometheus, and Grafana
V10 governed retraining, comparison, approval, local serving update, and rollback
```

## Production Engineering Highlights

### Reproducibility

```text
versioned dataset metadata
schema versioning
config snapshots
fixed random state
training metadata
MLflow run lineage
```

### Safety

```text
data validation gate
candidate-vs-production comparison
regression protection
human approval
promotion records
rollback target persistence
post-update readiness and prediction validation
registry restoration after failed mutation
```

### Observability

```text
structured runtime logs
prediction telemetry
failure categorization
monitoring summaries
drift reports
Prometheus metrics
Grafana dashboard
incident workflow
```

### Deployment

```text
Dockerized FastAPI service
manual GitHub Actions deployment controls
Workload Identity Federation
Artifact Registry image publishing
Cloud Run revision deployment
external /health validation
rollback and cleanup guidance
```

## Governed Retraining Story

V10 uses V9 monitoring outputs as decision inputs:

```text
monitoring alerts + drift summary
-> retraining recommendation
-> candidate run initialization
-> validation and training
-> candidate-vs-production metrics
-> regression gates
-> human approval
-> promotion decision
-> local serving handoff
-> local champion update
-> readiness and prediction validation
-> validated rollback
```

The workflow intentionally avoids blind automatic promotion.

## Evidence

Committed evidence:

```text
version implementation docs
verification logs
architecture diagrams
deployment validation records
learning guides
focused tests
```

Generated local evidence:

```text
monitoring reports
drift summaries
retraining run records
candidate artifacts
comparison report
approval record
promotion record
serving update report
rollback report
```

Generated runtime evidence is ignored by Git to avoid committing mutable local artifacts.

## Engineering Trade-Offs

| Decision | Benefit | Trade-Off |
|---|---|---|
| scikit-learn baseline | inspectable and fast | limited model complexity |
| local filesystem registry | transparent lifecycle learning | not a distributed production registry |
| Prefect orchestration | low local overhead | no managed scheduler deployment |
| human promotion approval | safer model evolution | less automation |
| Cloud Run | simple revisioned deployment | local model artifacts are not automatically cloud-ready |
| Prometheus and Grafana locally | production-style observability learning | no managed retention or alert routing |

## Current Limitations

```text
small synthetic dataset
local model and report storage
no production label feedback loop
no real concept drift calculation
no scheduled V10 retraining job
no automated Cloud Run model rollout after retraining
no fairness, calibration, or latency promotion gates
```

## Future Improvements

```text
external object storage for model artifacts
managed model registry
scheduled Prefect deployment
label feedback and concept drift
configurable metric tolerances
fairness and calibration gates
cloud retraining execution
canary Cloud Run deployment
managed monitoring and alert notifications
infrastructure as code
```

## Outcome

The project demonstrates more than model training. It demonstrates how operational ML components fit together, how model changes are governed, and how production mutations are validated and reversed.

