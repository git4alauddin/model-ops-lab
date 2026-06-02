# V1 Implementation

## Scope
Chunk V1-C1: project scaffolding only.
Chunk V1-C2: config validation and robust dataset loading.
Chunk V1-C3: feature-target split.
Chunk V1-C4: train-test split.
Chunk V1-C5: feature type detection.
Chunk V1-C6: preprocessing pipeline construction.
Chunk V1-C7: baseline model training.

## Folder Structure
Established `app/`, `configs/`, `data/`, `artifacts/`, and documentation hierarchy under `docs/`.
Added `docs/versions/v1/commit_log.md` to connect V1 implementation progress with git history.
Tests follow `tests/test_v1_cX_<component>.py` naming so each test file maps to a version component.

## Important Modules
- `app/train.py`: training entrypoint scaffold
- `app/evaluate.py`: evaluation entrypoint scaffold
- `app/config.py`: YAML config loader scaffold
- `app/utils/logger.py`: basic logging setup
- `app/utils/artifacts.py`: artifact directory helper

## V1-C2 Additions
- `app/config.py`
  - added `ConfigError`
  - added validation for required keys and training constraints
  - added controlled YAML/file parsing failures
- `app/schemas.py`
  - defined required config key contracts
- `app/train.py`
  - added `DataError`
  - added robust CSV loading with controlled missing/corrupt/empty handling
  - added target column presence check
  - added dataset metadata logs (`rows`, `cols`, `target`)
  - added non-zero exit behavior on validation/load failure
- `tests/test_v1_c2_config_validation.py`
  - validates success path and key config failure paths
- `tests/test_v1_c2_dataset_loading.py`
  - validates missing/empty/success dataset loading behavior

## V1-C3 Additions
- `app/pipeline/preprocessing.py`
  - added `PreprocessingError`
  - added `split_features_target`
  - validates target presence before splitting
  - prevents datasets with no feature columns from passing forward
- `app/train.py`
  - uses `split_features_target` after dataset loading
  - logs feature column count and target row count
  - treats preprocessing validation failures as controlled bootstrap failures
- `tests/test_v1_c3_feature_target_split.py`
  - validates successful split
  - validates missing target failure
  - validates no-feature-column failure

## V1-C4 Additions
- `app/pipeline/preprocessing.py`
  - added `split_train_test`
  - validates matching feature/target row counts
  - validates non-empty split inputs
  - validates `test_size` before splitting
  - uses `random_state` for reproducible partitioning
- `app/train.py`
  - reads `test_size` and `random_state` from training config
  - creates train/test partitions after feature-target split
  - logs train/test row counts and split settings
- `tests/test_v1_c4_train_test_split.py`
  - validates expected split sizes
  - validates reproducibility with fixed random seed
  - validates mismatched feature/target length failure
  - validates invalid `test_size` failure

## V1-C5 Additions
- `app/pipeline/preprocessing.py`
  - added `identify_feature_types`
  - detects numeric feature columns
  - detects categorical feature columns
  - rejects empty feature dataframes
  - rejects unsupported feature dtypes instead of dropping them silently
- `app/train.py`
  - detects feature types from `x_train` after train-test split
  - logs numeric and categorical feature counts
- `tests/test_v1_c5_feature_type_detection.py`
  - validates mixed, numeric-only, and categorical-only feature detection
  - validates empty feature dataframe failure
  - validates unsupported dtype failure

## V1-C6 Additions
- `app/pipeline/preprocessing.py`
  - implemented `build_preprocessing_pipeline`
  - builds sklearn `ColumnTransformer`
  - applies `StandardScaler` to numeric features
  - applies `OneHotEncoder(handle_unknown="ignore")` to categorical features
  - rejects empty transformer configs
- `app/train.py`
  - builds preprocessing pipeline after feature type detection
  - logs enabled transformer groups
- `tests/test_v1_c6_preprocessing_pipeline.py`
  - validates mixed, numeric-only, and categorical-only pipeline construction
  - validates empty feature config failure
  - validates unknown categorical values do not break transformation

## V1-C7 Additions
- `app/pipeline/trainer.py`
  - added `TrainingError`
  - added `build_model`
  - added Logistic Regression baseline support
  - added `build_training_pipeline`
  - added `train_model` with training duration tracking
  - wraps training failures in controlled errors
- `app/train.py`
  - reads model config from `configs/training.yaml`
  - builds model after preprocessing pipeline construction
  - builds a full sklearn training pipeline
  - fits the pipeline on training data
  - logs model type, duration, and fitted step count
- `tests/test_v1_c7_baseline_model_training.py`
  - validates Logistic Regression model construction
  - validates unsupported model type failure
  - validates sklearn pipeline composition
  - validates successful training
  - validates controlled training failure

## Configs Used
- `configs/training.yaml` created with placeholder baseline settings.

## Commands Used
- directory creation with PowerShell `New-Item -ItemType Directory`.
- `python -m app.train` for bootstrap verification.
- `python -m pytest -q` for focused V1 unit verification.

## Trade-Offs
- Chose scaffolding-first to keep future chunks focused and verifiable.
- Kept schema validation lightweight (no external schema framework yet) to avoid premature complexity.
