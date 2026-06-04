# ModelOpsLab

Production-style, versioned MLOps project built incrementally.

## V1 Status

V1 is the baseline ML pipeline foundation. It now supports an end-to-end local training run:

- YAML-driven configuration
- robust CSV dataset loading
- configured non-feature column dropping
- feature-target split
- reproducible train/test split
- numeric and categorical feature detection
- sklearn preprocessing pipeline
- Logistic Regression baseline model training
- held-out evaluation metrics
- model, metrics, config snapshot, and metadata persistence
- readable console and file logs
- focused tests for each meaningful V1 component

## V2 Status

V2 is complete. The project now has a production-style data validation and quality layer:

- validation command scaffold
- validation package
- first versioned churn dataset schema
- validation report structure
- required and unexpected column checks
- datatype checks
- nullability checks
- null percentage checks
- numeric range checks
- outlier sanity checks
- allowed-value checks
- duplicate row and duplicate ID checks
- target distribution sanity checks
- validation report persistence
- validation metadata persistence
- training validation gate
- formatted validation runtime logs
- focused tests for each meaningful V2 component

## V3 Status

V3 is complete. The project now has dataset versioning and reproducibility foundations:

- dataset version registry folder
- first customer churn dataset version metadata file
- dataset registry metadata loader
- dataset registry metadata validation
- training metadata records dataset version information
- validation reports record dataset version information
- dataset registry records the dataset SHA256 checksum
- reproducibility check command verifies dataset checksum
- focused tests for dataset version metadata behavior

## V4 Status

V4 is in progress. The project is adding experiment tracking and training observability:

- MLflow dependency
- MLflow tracking configuration
- experiment tracking helper module
- MLflow run creation during training
- core parameter logging
- core metric logging
- training and evaluation duration metric logging
- artifact logging
- dedicated confusion matrix artifact logging
- MLflow run ID persistence in training metadata
- failed-run tagging for in-run training errors
- focused tests for experiment tracking helper behavior

## Setup

```powershell
python -m venv vir_env
.\vir_env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run Training

```powershell
python -m app.train
```

The default config uses:

- config: `configs/training.yaml`
- dataset: `data/churn.csv`
- dataset version: `data_versions/customer_churn/v1.yaml`
- target column: `churn`
- dropped column: `customer_id`
- model: Logistic Regression

## Run Tests

```powershell
python -m pytest -q
```

## Run Validation

```powershell
python -m app.validate_data
```

## Check Reproducibility

```powershell
python -m app.check_reproducibility
```

## Open MLflow UI

```powershell
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Then open:

```text
http://127.0.0.1:5000
```

## Runtime Outputs

Generated runtime files are intentionally ignored by git:

- `artifacts/model.pkl`
- `artifacts/metrics.json`
- `artifacts/confusion_matrix.json`
- `artifacts/config_snapshot.json`
- `artifacts/training_metadata.json`
- `reports/validation_report.json`
- `reports/validation_summary.txt`
- `logs/modelopslab.log`
- `mlflow.db`
- `mlruns/`

The repository keeps the artifact placeholder folder with `.gitkeep`, but trained models, metrics, metadata snapshots, and logs are local run outputs.

## Structure

```text
modelOpsLab/
  app/
    train.py
    validate_data.py
    check_reproducibility.py
    experiment_tracking.py
    evaluate.py
    config.py
    data.py
    schemas.py
    pipeline/
      preprocessing.py
      trainer.py
    utils/
      artifacts.py
      logger.py
    validation/
      checks.py
      reports.py
  configs/
    training.yaml
  schema_versions/
    customer_churn_v1.yaml
  data_versions/
    customer_churn/
      v1.yaml
  data/
    churn.csv
  artifacts/
    .gitkeep
  reports/
    .gitkeep
  tests/
    test_v1_*.py
    test_v2_*.py
    test_v3_*.py
  docs/
    versions/v1/
    versions/v2/
    versions/v3/
    versions/v4/
    architecture/
    decisions/
    experiments/
    incidents/
    deployment/
    observability/
    diagrams/
```

## V1 Workflow

```text
configs/training.yaml
  -> load and validate config
  -> load data/churn.csv
  -> drop configured non-feature columns
  -> split features and target
  -> create reproducible train/test split
  -> detect numeric and categorical features
  -> build preprocessing pipeline
  -> train Logistic Regression baseline
  -> evaluate on held-out test set
  -> persist model, metrics, config snapshot, and metadata
  -> write readable runtime logs
```
