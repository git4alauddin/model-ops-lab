# Technology Ownership Map

This guide lists the main technologies, tools, and concepts used in ModelOpsLab.

Use it as a conceptual checklist. The goal is not to memorize syntax. The goal is to know what each technology is responsible for, where it appears, and what mental model to carry while reading the code or docs.

## 1. Python Package And Command Structure

Where it appears:

```text
app/
python -m app.train
python -m app.run_experiments
python -m app.serve_api
```

Concepts to own:

```text
package
module
entrypoint
import path
__init__.py
```

Mental model:

```text
app/ is the project code package.
Top-level app/*.py files are mostly runnable commands.
Subfolders contain reusable implementation logic.
```

Common confusion:

```text
app/train.py is not just a helper file. It is also a command module when run with python -m app.train.
```

## 2. Configuration And Environment

Where it appears:

```text
configs/training.yaml
.env.example
app/config.py
app/serving/settings.py
deployment/docker-compose.yaml
```

Concepts to own:

```text
YAML config
environment variable
runtime default
path resolution
local vs container path
```

Mental model:

```text
YAML controls ML workflows.
Environment variables control serving/deployment runtime behavior.
```

Common confusion:

```text
configs/training.yaml controls local training and report paths.
.env.example controls serving container settings such as host, port, registry path, MLflow path, and log paths.
```

## 3. Pandas Data Handling

Where it appears:

```text
app/data.py
app/pipeline/preprocessing.py
app/validation/checks.py
```

Concepts to own:

```text
DataFrame
CSV loading
columns
dtypes
null values
feature/target split
```

Mental model:

```text
Pandas is the table layer.
The project loads CSV rows into a DataFrame, validates columns and values, then splits features from the target.
```

Common confusion:

```text
Validation checks the raw dataframe before training.
Preprocessing transforms feature columns after validation has passed.
```

## 4. Scikit-Learn

Where it appears:

```text
app/pipeline/preprocessing.py
app/pipeline/trainer.py
app/evaluate.py
app/serving/predictor.py
```

Concepts to own:

```text
train_test_split
ColumnTransformer
StandardScaler
OneHotEncoder
Pipeline
fit
predict
predict_proba
classification metrics
```

Mental model:

```text
Scikit-learn owns model preparation, training, and prediction.
The saved artifact is a full pipeline: preprocessing plus model.
```

Common confusion:

```text
The model artifact is not only Logistic Regression or Decision Tree.
It is a sklearn Pipeline containing preprocessing and the estimator.
```

## 5. Data Validation

Where it appears:

```text
schema_versions/customer_churn_v1.yaml
app/validation/checks.py
app/validation/reports.py
app/validate_data.py
app/train.py
```

Concepts to own:

```text
schema contract
required columns
unexpected columns
dtype checks
nullability
numeric ranges
allowed values
duplicate checks
quality checks
validation gate
```

Mental model:

```text
Validation decides whether data is allowed to reach training.
```

Important severity rule:

```text
ERROR or CRITICAL blocks training.
WARNING or INFO remains visible but does not block training.
```

## 6. Dataset Versioning And Reproducibility

Where it appears:

```text
data_versions/customer_churn/v1.yaml
app/dataset_registry.py
app/check_reproducibility.py
artifacts/training_metadata.json
reports/validation_report.json
```

Concepts to own:

```text
dataset registry
dataset version
metadata
lineage
checksum
SHA256
```

Mental model:

```text
Dataset version tells us which dataset was intended.
Checksum tells us whether the file content still matches that version.
```

Command to watch:

```powershell
python -m app.check_reproducibility
```

## 7. MLflow

Where it appears:

```text
app/experiment_tracking.py
app/train.py
app/run_experiments.py
mlflow.db
mlruns/
```

Concepts to own:

```text
experiment
run
run ID
params
metrics
artifacts
tags
tracking URI
```

Mental model:

```text
MLflow records experiment evidence.
It answers: what training runs happened and what did they produce?
```

Common confusion:

```text
MLflow champion tag is an experiment result.
The model registry champion is a lifecycle decision.
```

## 8. Champion Selection

Where it appears:

```text
app/champion_selection.py
reports/champion_run.json
docs/experiments/best_run_selection_rule.md
```

Concepts to own:

```text
eligible run
primary metric
tie-breaker
rejected run
champion report
```

Mental model:

```text
Champion selection picks the best eligible experiment run.
It does not automatically approve or deploy the model.
```

## 9. Model Registry

Where it appears:

```text
app/model_registry.py
app/register_model.py
app/promote_model.py
app/query_model_registry.py
app/rollback_model.py
model_registry/
```

Concepts to own:

```text
candidate
champion
archived
model version
promotion
rollback
single champion rule
```

Mental model:

```text
The registry records model lifecycle state.
It answers: which model version is candidate, champion, or archived?
```

Important boundary:

```text
Registry champion does not automatically mean deployed or served.
Serving must load the champion artifact.
```

## 10. Prefect

Where it appears:

```text
app/orchestration/prefect_pipeline.py
app/run_prefect_pipeline.py
prefect.yaml
docs/deployment/prefect_local_deployment.md
```

Concepts to own:

```text
flow
task
retry
deployment
work pool
schedule
```

Mental model:

```text
Prefect gives workflow visibility around validation, experiment, and finalization stages.
```

Important boundary:

```text
The schedule exists but is inactive by default.
The plain Python pipeline remains available.
```

## 11. FastAPI

Where it appears:

```text
app/serve_api.py
app/api/app.py
app/api/routes.py
```

Concepts to own:

```text
app factory
route
endpoint
HTTP method
status code
request
response
```

Mental model:

```text
FastAPI exposes the local champion model through HTTP endpoints.
```

Endpoints:

```text
GET /health
GET /ready
GET /metrics
POST /predict
POST /predict/batch
```

## 12. Pydantic

Where it appears:

```text
app/api/schemas.py
app/api/validation_handlers.py
```

Concepts to own:

```text
request schema
response schema
field constraint
validation error
422 response
```

Mental model:

```text
Pydantic is the API contract guard.
Invalid request payloads are rejected before model loading or prediction runs.
```

Common confusion:

```text
422 means schema validation failed.
503 means the model was unavailable.
500 means prediction execution failed after the request was valid.
```

## 13. Serving Readiness And Model Loading

Where it appears:

```text
app/serving/readiness.py
app/serving/model_loader.py
app/serving/predictor.py
```

Concepts to own:

```text
health
readiness
champion lookup
artifact URI
joblib loading
prediction smoke test
```

Mental model:

```text
Health says the API process is alive.
Readiness says the service can find and load the model it needs.
```

## 14. Logging And Prediction Telemetry

Where it appears:

```text
logs/modelopslab.log
logs/predictions.jsonl
app/serving/runtime_logging.py
app/serving/prediction_logging.py
app/observability/prediction_telemetry.py
```

Concepts to own:

```text
runtime log
JSONL
event_version
event_type
request_id
latency
deployment_version
failure_stage
```

Mental model:

```text
modelopslab.log is human-readable runtime history.
predictions.jsonl is structured telemetry for monitoring and drift.
```

## 15. Monitoring And Alerting

Where it appears:

```text
app/observability/monitoring_summary.py
app/observability/monitoring_alerts.py
reports/monitoring/
```

Concepts to own:

```text
request count
failure rate
p95 latency
prediction distribution
skipped telemetry
alert threshold
recommended action
```

Mental model:

```text
Monitoring converts raw telemetry into operational signals.
Alerts convert those signals into attention-worthy states.
```

Important boundary:

```text
V9 writes alert reports.
It does not page, notify Slack, or auto-remediate.
```

## 16. Data Drift

Where it appears:

```text
app/observability/drift_baseline.py
app/observability/inference_snapshot.py
app/observability/drift_comparison.py
reports/drift/
```

Concepts to own:

```text
reference baseline
inference snapshot
data drift
feature drift
numeric mean change
range expansion
categorical ratio change
insufficient data
```

Mental model:

```text
Drift checks whether prediction-time input features look different from training-time input features.
```

Important boundary:

```text
This is data drift, not concept drift.
It does not prove the model is wrong.
It says the model is receiving a different kind of input population.
```

## 17. Dashboard Artifacts

Where it appears:

```text
app/observability/dashboard_snapshot.py
app/observability/monitoring_dashboard.py
reports/monitoring/dashboard_snapshot.json
reports/monitoring/dashboard.html
```

Concepts to own:

```text
dashboard data contract
static HTML dashboard
report freshness
summary cards
distribution sections
```

Mental model:

```text
The snapshot combines multiple reports.
The HTML file renders the snapshot for local visual inspection.
```

## 18. Prometheus

Where it appears:

```text
app/api/routes.py
app/observability/prometheus_metrics.py
deployment/monitoring/prometheus/prometheus.yml
```

Concepts to own:

```text
metrics endpoint
scrape
target
Prometheus text format
time series
```

Mental model:

```text
FastAPI exposes /metrics.
Prometheus repeatedly scrapes /metrics and stores time-series values.
```

## 19. Grafana

Where it appears:

```text
deployment/docker-compose.monitoring.yaml
deployment/monitoring/grafana/
docs/monitoring/grafana_prometheus_local_stack.md
```

Concepts to own:

```text
datasource
dashboard
panel
query
provisioning
```

Mental model:

```text
Grafana visualizes metrics stored in Prometheus.
The project provisions the datasource and dashboard through files.
```

## 20. Docker

Where it appears:

```text
deployment/Dockerfile
.dockerignore
deployment/docker-compose.yaml
deployment/docker-compose.monitoring.yaml
```

Concepts to own:

```text
image
container
Dockerfile
build context
.dockerignore
port mapping
environment variable
volume mount
read-only volume
```

Mental model:

```text
Docker image is the packaged app.
Container is a running instance of that image.
Volumes supply runtime state that should not be baked into the image.
```

Common confusion:

```text
model_registry/ and mlruns/ are excluded from the image but mounted into the local serving container.
```

## 21. Docker Compose

Where it appears:

```text
deployment/docker-compose.yaml
deployment/docker-compose.monitoring.yaml
```

Concepts to own:

```text
service
ports
volumes
environment
env_file
depends_on
restart
extra_hosts
```

Mental model:

```text
Compose defines how multiple containers or local runtime pieces run together.
```

Serving Compose:

```text
FastAPI serving API
local model registry mount
local MLflow artifacts mount
writable logs mount
```

Monitoring Compose:

```text
Prometheus service
Grafana service
provisioned datasource
provisioned dashboard
```

## 22. GitHub Actions

Where it appears:

```text
.github/workflows/ci.yaml
docs/deployment/
```

Concepts to own:

```text
workflow
trigger
workflow_dispatch
input
job
step
runner
checkout
setup-python
dependency install
pytest gate
Docker build gate
job dependency
secret
conditional step
```

Mental model:

```text
GitHub Actions is the automation runner for tests, Docker builds, image publishing, and manually gated Cloud Run deployment.
```

Important gates:

```text
tests must pass before Docker image build
image publishing is manual
Cloud Run deployment is manual
Cloud Run deploy uses a specific Git SHA image
```

## 23. Container Registries

Where it appears:

```text
Docker Hub docs
Artifact Registry docs
.github/workflows/ci.yaml
deployment/image_tags.md
```

Concepts to own:

```text
image registry
image tag
Git SHA tag
digest
push
pull
fallback registry
preferred registry
```

Mental model:

```text
A registry stores Docker images so deployment platforms can pull them.
Git SHA tags make image identity traceable.
```

Project choice:

```text
Artifact Registry is the preferred GCP-native image source.
Docker Hub remains a fallback path.
```

## 24. Google Cloud Run

Where it appears:

```text
docs/deployment/cloud_run_*.md
.github/workflows/ci.yaml
```

Concepts to own:

```text
service
revision
container image
container port
environment variable
public URL
traffic
health check
rollback
```

Mental model:

```text
Cloud Run runs the serving container as a managed HTTP service.
Each deployment creates a revision.
Rollback means routing traffic back to a known-good revision or image.
```

Important boundary:

```text
V8 validates Cloud Run /health.
It does not validate live /ready or /predict with external model artifacts.
```

## 25. Workload Identity Federation

Where it appears:

```text
docs/learning/workload_identity_federation_notes.md
.github/workflows/ci.yaml
```

Concepts to own:

```text
OIDC
identity pool
provider
service account
impersonation
short-lived credentials
IAM role
```

Mental model:

```text
GitHub Actions gets short-lived permission to act as a Google Cloud service account.
No long-lived service account key is stored in the repo.
```

## 26. Pytest

Where it appears:

```text
tests/
.github/workflows/ci.yaml
```

Concepts to own:

```text
unit test
contract test
fixture
monkeypatch
focused test
static documentation test
full suite
```

Mental model:

```text
Tests encode the project contracts.
For ownership, tests often explain expected behavior faster than implementation code.
```

## 27. Governance And Continuous ML Lifecycle

Where it appears:

```text
docs/retraining/
app/retraining/
retraining_runs/
docs/architecture/continuous_ml_lifecycle.md
```

Concepts to own:

```text
trigger
candidate retraining
comparison
regression gate
human approval
promotion record
serving handoff
rollback target
audit evidence
```

Mental model:

```text
V10 prevents blind replacement.
Every model-evolution step leaves evidence before serving state changes.
```

Core safety chain:

```text
signal
-> retraining decision
-> candidate training
-> comparison
-> approval
-> promotion record
-> serving handoff
-> local serving update
-> validation
-> rollback path
```

## Fast Review Order

If you need to refresh the project quickly, use this order:

```text
1. Python package and commands
2. Config and environment
3. Pandas and scikit-learn
4. Validation and dataset versioning
5. MLflow and champion selection
6. Model registry
7. FastAPI serving and Pydantic schemas
8. Logging, telemetry, monitoring, and drift
9. Docker and Docker Compose
10. GitHub Actions, registries, Cloud Run, and WIF
11. Prefect orchestration
12. V10 governance lifecycle
```

