# ModelOpsLab

Production-style, versioned MLOps project built incrementally.

The project starts with a local ML training pipeline and gradually adds validation, reproducibility, experiment tracking, orchestration, model lifecycle management, serving, and deployment foundations.

## Current Scope

| Version | Focus |
|---|---|
| V1 | Baseline local training pipeline |
| V2 | Data validation and training gate |
| V3 | Dataset versioning and reproducibility |
| V4 | MLflow experiment tracking and champion selection |
| V5 | Local orchestration with Prefect |
| V6 | Model registry and model lifecycle foundations |
| V7 | FastAPI model serving |
| V8 | Dockerization and deployment foundations |
| V9 | Monitoring, drift detection, and production observability |

Detailed implementation history lives under `docs/versions/`.

## Setup

```powershell
python -m venv vir_env
.\vir_env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Main Commands

Run tests:

```powershell
python -m pytest -q
```

Run data validation:

```powershell
python -m app.validate_data
```

Run baseline training:

```powershell
python -m app.train
```

Run multi-model experiments:

```powershell
python -m app.run_experiments
```

Run the plain training pipeline:

```powershell
python -m app.run_training_pipeline
```

Run the Prefect training pipeline locally:

```powershell
python -m app.run_prefect_pipeline
```

Run the FastAPI serving API locally:

```powershell
uvicorn app.serve_api:app --reload
```

Build local prediction monitoring summary:

```powershell
python -m app.build_prediction_monitoring_summary
```

The summary uses supported V9 telemetry events and reports skipped legacy records.

Build local monitoring alerts:

```powershell
python -m app.build_monitoring_alerts
```

Build drift reference baseline:

```powershell
python -m app.build_drift_reference_baseline
```

Build inference feature snapshot:

```powershell
python -m app.build_inference_snapshot
```

Build local data drift summary:

```powershell
python -m app.build_data_drift_summary
```

Build dashboard-ready monitoring snapshot:

```powershell
python -m app.build_dashboard_snapshot
```

Check dataset reproducibility:

```powershell
python -m app.check_reproducibility
```

Build the serving Docker image:

```powershell
docker build -f deployment/Dockerfile -t modelopslab-serving:v8-c1 .
```

Run the serving Docker image:

```powershell
docker run --rm -p 8000:8000 modelopslab-serving:v8-c1
```

Run the serving API with Docker Compose:

```powershell
docker compose -f deployment/docker-compose.yaml --env-file .env.example up --build
```

Serving environment defaults live in `.env.example`.

## MLflow UI

Start the local MLflow UI:

```powershell
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Open:

```text
http://127.0.0.1:5000
```

## Important Outputs

Generated runtime files are intentionally local and ignored by git:

| Path | Purpose |
|---|---|
| `artifacts/` | trained model, metrics, config snapshot, training metadata |
| `reports/` | validation reports and champion selection report |
| `reports/monitoring/prediction_summary.json` | local prediction monitoring summary |
| `reports/monitoring/alerts.json` | local monitoring alert report |
| `reports/monitoring/dashboard_snapshot.json` | dashboard-ready monitoring and drift snapshot |
| `reports/drift/reference_baseline.json` | training-data reference baseline for drift checks |
| `reports/drift/inference_snapshot.json` | production inference feature snapshot for drift checks |
| `reports/drift/data_drift_summary.json` | local baseline-vs-inference drift summary |
| `logs/` | local runtime logs |
| `mlflow.db` | MLflow backend database |
| `mlruns/` | MLflow run artifacts |
| `pipeline_runs/` | pipeline-level run metadata |

## Useful Docs

| Topic | Location |
|---|---|
| Version history | `docs/versions/` |
| Architecture notes | `docs/architecture/` |
| Decision records | `docs/decisions/` |
| Experiment tracking docs | `docs/experiments/` |
| Deployment notes | `docs/deployment/` |
| Flow diagrams | `docs/diagrams/` |

Manual CI run guide:

```text
docs/deployment/ci_manual_run_guide.md
```

Docker Hub publishing plan:

```text
docs/deployment/dockerhub_publishing_plan.md
```

Docker Hub secrets setup:

```text
docs/deployment/dockerhub_secrets_setup.md
```

Docker Hub publish run guide:

```text
docs/deployment/dockerhub_publish_run_guide.md
```

Cloud Run GitHub Actions deployment guide:

```text
docs/deployment/cloud_run_github_actions_deploy.md
```

Cloud Run live validation:

```text
docs/deployment/cloud_run_live_validation.md
```

Artifact Registry foundation:

```text
docs/deployment/artifact_registry_foundation.md
```

Artifact Registry setup validation:

```text
docs/deployment/artifact_registry_setup_validation.md
```

Artifact Registry publish gate:

```text
docs/deployment/artifact_registry_publish_gate.md
```

Artifact Registry publish validation:

```text
docs/deployment/artifact_registry_publish_validation.md
```

Cloud Run image source gate:

```text
docs/deployment/cloud_run_image_source_gate.md
```

Cloud Run Artifact Registry deployment validation:

```text
docs/deployment/cloud_run_artifact_registry_deploy_validation.md
```

Artifact Registry default deploy source:

```text
docs/deployment/artifact_registry_default_deploy_source.md
```

Cloud Run rollback and cleanup guide:

```text
docs/deployment/cloud_run_rollback_cleanup_guide.md
```

V9 observability strategy:

```text
docs/monitoring/observability_strategy.md
```

Prediction telemetry contract:

```text
docs/monitoring/prediction_telemetry_contract.md
```

Fresh feature telemetry workflow:

```text
docs/monitoring/fresh_feature_telemetry_workflow.md
```

Workload Identity Federation learning notes:

```text
docs/learning/workload_identity_federation_notes.md
```

Manual CI Cloud Run trigger learning notes:

```text
docs/learning/manual_ci_cloud_run_trigger_notes.md
```

V8 closure:

```text
docs/versions/v8/closure.md
```

## Project Structure

```text
modelOpsLab/
  app/                 # application code
  configs/             # training configuration
  data/                # local sample data
  data_versions/       # dataset version metadata
  schema_versions/     # validation schema versions
  tests/               # versioned test suite
  docs/                # project documentation
  deployment/          # Docker and deployment assets
  artifacts/           # local runtime artifacts
  reports/             # local runtime reports
  logs/                # local logs
  mlruns/              # MLflow artifact store
  pipeline_runs/       # pipeline run metadata
```
