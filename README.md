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

V2 has started with the data validation foundation:

- validation command scaffold
- validation package
- first versioned churn dataset schema
- validation report structure
- required and unexpected column checks
- focused validation foundation tests

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

## Runtime Outputs

Generated runtime files are intentionally ignored by git:

- `artifacts/model.pkl`
- `artifacts/metrics.json`
- `artifacts/config_snapshot.json`
- `artifacts/training_metadata.json`
- `logs/modelopslab.log`

The repository keeps the artifact placeholder folder with `.gitkeep`, but trained models, metrics, metadata snapshots, and logs are local run outputs.

## Structure

```text
modelOpsLab/
  app/
    train.py
    validate_data.py
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
  data/
    churn.csv
  artifacts/
    .gitkeep
  tests/
    test_v1_c2_config_validation.py
    test_v1_c2_dataset_loading.py
    test_v1_c3_feature_target_split.py
    test_v1_c4_train_test_split.py
    test_v1_c5_feature_type_detection.py
    test_v1_c6_preprocessing_pipeline.py
    test_v1_c7_baseline_model_training.py
    test_v1_c8_sample_churn_dataset.py
    test_v1_c9_evaluation_metrics.py
    test_v1_c10_artifact_persistence.py
    test_v1_c11_file_logging.py
    test_v2_c1_validation_foundation.py
  docs/
    versions/v1/
    versions/v2/
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
