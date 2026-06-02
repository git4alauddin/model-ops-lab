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

## Pending - v1-c6: build preprocessing pipeline

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
