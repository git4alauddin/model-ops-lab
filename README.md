# ModelOpsLab

Production-style, versioned MLOps project built incrementally.

The project starts with a local ML training pipeline and gradually adds validation, reproducibility, experiment tracking, orchestration, and model lifecycle management.

## Current Scope

| Version | Focus |
|---|---|
| V1 | Baseline local training pipeline |
| V2 | Data validation and training gate |
| V3 | Dataset versioning and reproducibility |
| V4 | MLflow experiment tracking and champion selection |
| V5 | Local orchestration with Prefect |
| V6 | Model registry and model lifecycle foundations |

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

Check dataset reproducibility:

```powershell
python -m app.check_reproducibility
```

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
  artifacts/           # local runtime artifacts
  reports/             # local runtime reports
  logs/                # local logs
  mlruns/              # MLflow artifact store
  pipeline_runs/       # pipeline run metadata
```
