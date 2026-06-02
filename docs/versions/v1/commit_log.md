# V1 Commit Log

This file records meaningful V1 commits and the operational purpose of each change.

## 2367f8c - v1: scaffold baseline pipeline, config, and documentation structure

### What Changed
- Created the initial V1 project structure under `app/`, `configs/`, `data/`, `artifacts/`, and `docs/`.
- Added training and evaluation entrypoint scaffolds.
- Added config, schema, preprocessing, trainer, logger, and artifact utility scaffolds.
- Added `configs/training.yaml`, `requirements.txt`, `.env.example`, and base README structure.
- Created V1 documentation files under `docs/versions/v1/`.

### What Problem It Solved
- Established a stable repository shape before adding ML pipeline logic.
- Created the required documentation structure from `doc_strategy.txt`.
- Prevented implementation work from starting in an unstructured layout.

### Verification
- Confirmed scaffold files and folders existed.
- Confirmed git tracked the intended structure without tracking the virtual environment.

## abbb8eb - v1: add config and data ingestion validation with focused tests

### What Changed
- Added YAML config loading and validation in `app/config.py`.
- Added required config key contracts in `app/schemas.py`.
- Added robust CSV loading in `app/train.py`.
- Added controlled failure handling for missing config, invalid config, missing dataset, corrupted CSV, empty dataset, and missing target column.
- Added focused tests for config validation and dataset loading.
- Added `pytest` to `requirements.txt`.
- Updated V1 implementation, verification, issues, and lessons docs.

### What Problem It Solved
- Made the training bootstrap config-driven instead of hardcoded.
- Added safe dataset ingestion before training logic.
- Made early failures explicit and debuggable.
- Locked the first focused test pattern for V1.

### Verification
- `python -m pytest -q` passed after interpreter alignment.
- `python -m app.train` failed with controlled `Dataset file not found: data\churn.csv`, which was expected because no real dataset exists yet.

## 8814d9a - v1: add preprocessing splits with focused tests

### What Changed
- Added `PreprocessingError` and `split_features_target` in `app/pipeline/preprocessing.py`.
- Updated `app/train.py` to split features and target after dataset loading.
- Added logging for feature column count and target row count.
- Added focused tests for successful split, missing target, and no-feature-column failure.
- Added `split_train_test` in `app/pipeline/preprocessing.py`.
- Updated `app/train.py` to create train/test partitions after feature-target split.
- Added logging for train rows, test rows, configured `test_size`, and `random_state`.
- Added focused tests for expected split sizes, reproducible split indexes, mismatched row counts, and invalid `test_size`.
- Added `docs/versions/v1/commit_log.md`.
- Updated README and V1 documentation.

### What Problem It Solved
- Prevents target leakage by centralizing feature-target separation.
- Blocks invalid datasets where no feature columns remain after target split.
- Moves preprocessing responsibility out of the training entrypoint.
- Makes training partitioning config-driven and reproducible.
- Establishes the train/test boundary needed before preprocessing pipeline fitting and baseline model training.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `13 passed in 2.55s`.
- `.\vir_env\Scripts\python.exe -m app.train` still fails with controlled missing dataset error, as expected before adding real data.

## 2acea0f - v1-c5: add feature type detection with focused tests

### What Changed
- Added `identify_feature_types` in `app/pipeline/preprocessing.py`.
- Updated `app/train.py` to detect feature types from `x_train`.
- Added logging for numeric and categorical feature counts.
- Added focused tests for mixed, numeric-only, categorical-only, empty, and unsupported feature columns.
- Updated README and V1 documentation.

### What Problem It Solved
- Determines which columns should be scaled or encoded before building the preprocessing pipeline.
- Prevents unsupported feature dtypes from being silently dropped.
- Keeps feature typing logic centralized in preprocessing instead of the training entrypoint.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `18 passed in 1.34s`.
- `.\vir_env\Scripts\python.exe -m app.train` still fails with controlled missing dataset error, as expected before adding real data.

## 4245035 - v1-c6: build preprocessing pipeline with focused tests

### What Changed
- Implemented `build_preprocessing_pipeline` in `app/pipeline/preprocessing.py`.
- Added sklearn `ColumnTransformer` construction.
- Added `StandardScaler` for numeric feature columns.
- Added `OneHotEncoder(handle_unknown="ignore")` for categorical feature columns.
- Updated `app/train.py` to build and log the preprocessing pipeline after feature type detection.
- Added focused preprocessing pipeline tests.
- Renamed V1 tests to the component-aware convention `tests/test_v1_cX_<component>.py`.
- Updated README and V1 documentation.

### What Problem It Solved
- Creates the reusable preprocessing object required before baseline model training.
- Keeps scaling and encoding logic centralized in the preprocessing module.
- Prevents unknown categorical values from breaking transformation.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `23 passed in 1.32s`.
- `.\vir_env\Scripts\python.exe -m app.train` still fails with controlled missing dataset error, as expected before adding real data.

## 5f0a604 - v1-c7: add baseline model training with focused tests

### What Changed
- Implemented baseline training helpers in `app/pipeline/trainer.py`.
- Added Logistic Regression model construction from config.
- Added full sklearn training pipeline composition with preprocessing and model steps.
- Added controlled `TrainingError` handling.
- Added training duration tracking.
- Updated `app/train.py` to train the fitted pipeline after preprocessing pipeline construction.
- Cleaned `app/train.py` static inspection issues with typed config extraction, used split outputs, and shorter log strings.
- Added focused baseline model training tests.
- Updated README and V1 documentation.

### What Problem It Solved
- Turns the prepared train/test data and preprocessing pipeline into an actual fitted baseline model.
- Keeps model construction and fitting logic out of the training entrypoint.
- Establishes the first reusable training pipeline needed before evaluation and artifact persistence.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `28 passed in 1.27s` after the train entrypoint cleanup.
- `.\vir_env\Scripts\python.exe -m app.train` still fails with controlled missing dataset error, as expected before adding real data.

## 7486fa2 - v1-c8: add sample churn dataset smoke run

### What Changed
- Added `data/churn.csv` as a small synthetic binary churn dataset.
- Added `dataset.drop_columns` to `configs/training.yaml`.
- Configured `customer_id` to be dropped before training.
- Added `drop_configured_columns` in `app/train.py`.
- Updated training flow to drop configured non-feature columns before feature-target split.
- Added focused tests for sample dataset loading and configured column dropping.
- Made the sample dataset test resolve `data/churn.csv` from the project root so IDE working directories do not break it.
- Updated README and V1 documentation.

### What Problem It Solved
- Allows `python -m app.train` to prove the success path instead of only controlled failure handling.
- Provides a stable V1 smoke dataset for local training verification.
- Prevents identifier columns from entering model features.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `31 passed in 1.32s`.
- `.\vir_env\Scripts\python.exe -m pytest tests\test_v1_c8_sample_churn_dataset.py -q` returned `3 passed in 1.18s` after the path-stability fix.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `31 passed in 1.33s` after the path-stability fix.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully using `data/churn.csv`.
- Training logs showed `rows=20`, `train_rows=16`, `test_rows=4`, `numeric_features=3`, `categorical_features=4`, and `fitted_steps=2`.

## a2686e2 - v1-c9: add evaluation metrics with focused tests

### What Changed
- Implemented evaluation helpers in `app/evaluate.py`.
- Added `EvaluationError`.
- Added accuracy, precision, recall, F1 score, and confusion matrix calculation.
- Updated `app/train.py` to evaluate the fitted pipeline on the test set.
- Added evaluation metric logging.
- Added focused tests for metric structure, numeric metric values, confusion matrix shape, mismatched test input, and missing predict method.
- Carried the c8 sample dataset test path-stability fix into this pending commit.
- Updated README and V1 documentation.

### What Problem It Solved
- Adds the first model quality measurement layer to the V1 training workflow.
- Ensures evaluation uses held-out test data instead of training data.
- Produces a structured metrics dictionary that can be persisted in the next artifact step.

### Verification
- Initial `.\vir_env\Scripts\python.exe -m pytest -q` run returned `1 failed, 35 passed` because a tiny test split produced a `1x1` confusion matrix.
- Fixed evaluation by passing explicit binary labels `[0, 1]` to `confusion_matrix`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `36 passed in 1.35s`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and logged accuracy, precision, recall, F1, and a stable `2x2` confusion matrix.

## Pending - v1-c10: persist metrics and training artifacts

### What Changed
- Implemented artifact persistence helpers in `app/utils/artifacts.py`.
- Added model artifact persistence using `joblib`.
- Added JSON persistence for metrics, config snapshot, and training metadata.
- Updated `app/train.py` to persist artifacts after evaluation.
- Added generated artifact paths to runtime logs.
- Updated `.gitignore` to ignore generated artifact files while preserving `artifacts/.gitkeep`.
- Added focused artifact persistence tests.
- Updated README and V1 documentation.

### What Problem It Solved
- Makes successful training runs inspectable after the command finishes.
- Persists the fitted preprocessing-plus-model pipeline for reuse.
- Captures metrics, config, and metadata needed for reproducibility and debugging.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `40 passed in 1.74s`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully.
- Training generated `artifacts/model.pkl`, `artifacts/metrics.json`, `artifacts/config_snapshot.json`, and `artifacts/training_metadata.json`.
- Generated artifact files are ignored by git while `artifacts/.gitkeep` remains tracked.
