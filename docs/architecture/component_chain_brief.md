# Component Chain Brief

This is the fast conceptual map of ModelOpsLab.

Use it when you need to explain the project quickly without opening code.

## One-Line Project View

```text
ModelOpsLab trains, validates, tracks, registers, serves, deploys, monitors, retrains, and rolls back a churn model through a local-first MLOps lifecycle.
```

## Core Chain

```text
config
-> data
-> validation
-> training
-> evaluation
-> artifacts
-> experiment tracking
-> champion selection
-> model registry
-> serving API
-> container deployment
-> prediction telemetry
-> monitoring and drift
-> retraining decision
-> candidate retraining
-> comparison and approval
-> local serving update
-> rollback
```

## Component Map

## 1. Config

Main files:

```text
configs/training.yaml
app/config.py
```

Role:

```text
Defines dataset path, target column, split settings, model settings, artifact paths, validation schema, MLflow settings, and candidate models.
```

Hands off to:

```text
data loading
validation
training
experiment tracking
artifact persistence
```

## 2. Data

Main files:

```text
data/churn.csv
app/data.py
```

Role:

```text
Provides the source CSV and loads it safely into a dataframe.
```

Hands off to:

```text
validation
feature/target split
training
drift reference baseline
```

## 3. Validation

Main files:

```text
schema_versions/customer_churn_v1.yaml
app/validate_data.py
app/validation/checks.py
app/validation/reports.py
```

Role:

```text
Checks whether the dataset is structurally valid and safe enough for training.
```

Decision:

```text
ERROR or CRITICAL blocks training.
WARNING or INFO stays visible but does not block.
```

Outputs:

```text
reports/validation_report.json
reports/validation_summary.txt
```

Hands off to:

```text
training gate
pipeline orchestration
candidate retraining validation
```

## 4. Dataset Versioning

Main files:

```text
data_versions/customer_churn/v1.yaml
app/dataset_registry.py
app/check_reproducibility.py
```

Role:

```text
Records which dataset version is active and verifies that the local CSV content still matches using SHA256 checksum.
```

Outputs:

```text
dataset version snapshot
checksum validation result
```

Hands off to:

```text
training metadata
validation reports
MLflow params
model registry metadata
retraining lineage
```

## 5. Training

Main files:

```text
app/train.py
app/pipeline/preprocessing.py
app/pipeline/trainer.py
app/evaluate.py
```

Role:

```text
Builds the local sklearn training pipeline: split data, preprocess features, train model, evaluate metrics.
```

Outputs:

```text
artifacts/model.pkl
artifacts/metrics.json
artifacts/confusion_matrix.json
artifacts/config_snapshot.json
artifacts/training_metadata.json
logs/modelopslab.log
```

Hands off to:

```text
MLflow tracking
experiment comparison
model registry
serving loader
```

## 6. Experiment Tracking

Main files:

```text
app/experiment_tracking.py
app/run_experiments.py
app/champion_selection.py
docs/experiments/best_run_selection_rule.md
```

Role:

```text
Runs candidate models, logs params/metrics/artifacts to MLflow, compares eligible runs, and selects an experiment champion.
```

Outputs:

```text
mlflow.db
mlruns/
reports/champion_run.json
artifacts/experiments/<candidate>/
```

Hands off to:

```text
model registration
pipeline metadata
portfolio evidence
```

## 7. Pipeline Orchestration

Main files:

```text
app/run_training_pipeline.py
app/run_prefect_pipeline.py
app/tasks/
app/orchestration/prefect_pipeline.py
prefect.yaml
```

Role:

```text
Wraps validation and experiment stages into a pipeline with stage-level metadata and optional local Prefect visibility.
```

Outputs:

```text
pipeline_runs/<pipeline_run_id>.json
```

Hands off to:

```text
experiment tracking
champion selection
pipeline audit evidence
```

## 8. Model Registry

Main files:

```text
app/model_registry.py
app/register_model.py
app/promote_model.py
app/query_model_registry.py
app/rollback_model.py
model_registry/
```

Role:

```text
Turns an experiment champion into a managed model version with lifecycle state.
```

States:

```text
candidate
champion
archived
```

Outputs:

```text
model_registry/<model_name>__<model_version>.json
```

Hands off to:

```text
serving readiness
model loading
local retraining update
rollback
```

Important boundary:

```text
Registry stores model metadata and lifecycle state.
MLflow artifacts store the actual model.pkl.
```

## 9. Serving API

Main files:

```text
app/serve_api.py
app/api/routes.py
app/api/schemas.py
app/serving/
```

Role:

```text
Exposes the active local champion model through FastAPI endpoints.
```

Endpoints:

```text
GET /health
GET /ready
GET /metrics
POST /predict
POST /predict/batch
```

Runtime needs:

```text
model_registry/*.json
mlruns/.../artifacts/model.pkl
```

Outputs:

```text
prediction response JSON
logs/predictions.jsonl
logs/modelopslab.log
```

Hands off to:

```text
monitoring summary
drift inference snapshot
Prometheus metrics
incident debugging
```

## 10. Deployment

Main files:

```text
deployment/Dockerfile
deployment/docker-compose.yaml
.github/workflows/ci.yaml
docs/deployment/
```

Role:

```text
Packages the serving API into a Docker image, validates it in CI, publishes it, and deploys it to Cloud Run.
```

Outputs:

```text
Docker image
Artifact Registry image
Cloud Run service revision
Cloud Run /health URL
```

Important boundary:

```text
The Cloud Run image contains app code and dependencies.
It does not currently contain local model registry records or MLflow model artifacts.
```

## 11. Monitoring

Main files:

```text
app/observability/prediction_telemetry.py
app/observability/monitoring_summary.py
app/observability/monitoring_alerts.py
```

Role:

```text
Converts prediction telemetry into request, latency, failure, distribution, and alert signals.
```

Outputs:

```text
reports/monitoring/prediction_summary.json
reports/monitoring/alerts.json
```

Hands off to:

```text
dashboard snapshot
Prometheus metrics
retraining trigger decision
incident workflow
```

## 12. Drift Detection

Main files:

```text
app/observability/drift_baseline.py
app/observability/inference_snapshot.py
app/observability/drift_comparison.py
```

Role:

```text
Compares training-time feature distributions with prediction-time feature distributions.
```

Drift type:

```text
data drift / input feature drift
```

Outputs:

```text
reports/drift/reference_baseline.json
reports/drift/inference_snapshot.json
reports/drift/data_drift_summary.json
```

Hands off to:

```text
alerts
dashboard
retraining trigger decision
```

Important boundary:

```text
This does not detect concept drift because production labels are not available.
```

## 13. Dashboards And Metrics

Main files:

```text
app/observability/dashboard_snapshot.py
app/observability/monitoring_dashboard.py
app/observability/prometheus_metrics.py
deployment/docker-compose.monitoring.yaml
deployment/monitoring/
```

Role:

```text
Presents monitoring and drift signals through local HTML, /metrics, Prometheus, and Grafana.
```

Outputs:

```text
reports/monitoring/dashboard_snapshot.json
reports/monitoring/dashboard.html
GET /metrics
Prometheus time-series data
Grafana dashboard
```

Hands off to:

```text
incident debugging
operator decisions
retraining signal review
```

## 14. Retraining Governance

Main files:

```text
app/evaluate_retraining_trigger.py
app/retraining/
app/start_candidate_retraining_run.py
app/run_candidate_retraining.py
app/compare_candidate_to_production.py
app/record_retraining_approval.py
app/record_candidate_promotion.py
app/validate_serving_handoff.py
```

Role:

```text
Turns monitoring/drift signals into a controlled candidate retraining lifecycle with comparison, approval, and promotion evidence.
```

Outputs:

```text
reports/retraining/retraining_trigger_decision.json
retraining_runs/<run_id>/retraining_metadata.json
retraining_runs/<run_id>/candidate/
retraining_runs/<run_id>/comparison_report.json
retraining_runs/<run_id>/approval_record.json
retraining_runs/<run_id>/promotion_record.json
retraining_runs/<run_id>/serving_handoff_report.json
```

Hands off to:

```text
local registry and serving update
rollback
portfolio evidence
```

## 15. Local Serving Update And Rollback

Main files:

```text
app/update_local_serving_model.py
app/rollback_local_retraining_model.py
app/retraining/local_serving_update.py
app/retraining/local_serving_rollback.py
```

Role:

```text
Mutates local model registry champion state after all V10 gates pass and proves the change can be rolled back.
```

Forward update:

```text
archive previous champion
write retraining candidate as champion
validate readiness
run prediction smoke test
```

Rollback:

```text
archive retraining champion
restore previous champion
validate readiness
run prediction smoke test
```

Important boundary:

```text
Local serving update does not redeploy Cloud Run.
Cloud Run retraining rollout is deferred.
```

## System Memory Hooks

Use these files when you need quick orientation:

```text
docs/architecture/app_structure.md
docs/architecture/technology_ownership_map.md
docs/architecture/continuous_ml_lifecycle.md
docs/diagrams/v1_pipeline_flow.md
docs/diagrams/v10_retraining_flow.md
```

## Final Mental Model

```text
V1 builds the model.
V2 protects training from bad data.
V3 proves dataset identity.
V4 compares experiments.
V5 orchestrates the workflow.
V6 manages model lifecycle.
V7 serves the champion locally.
V8 deploys the API container.
V9 observes serving behavior and drift.
V10 governs retraining, local serving update, and rollback.
```

