# V1 Implementation

## Scope
Chunk V1-C1: project scaffolding only.
Chunk V1-C2: config validation and robust dataset loading.
Chunk V1-C3: feature-target split.
Chunk V1-C4: train-test split.

## Folder Structure
Established `app/`, `configs/`, `data/`, `artifacts/`, and documentation hierarchy under `docs/`.
Added `docs/versions/v1/commit_log.md` to connect V1 implementation progress with git history.

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
- `tests/test_v1_config_validation.py`
  - validates success path and key config failure paths
- `tests/test_v1_dataset_loading.py`
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
- `tests/test_v1_feature_target_split.py`
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
- `tests/test_v1_train_test_split.py`
  - validates expected split sizes
  - validates reproducibility with fixed random seed
  - validates mismatched feature/target length failure
  - validates invalid `test_size` failure

## Configs Used
- `configs/training.yaml` created with placeholder baseline settings.

## Commands Used
- directory creation with PowerShell `New-Item -ItemType Directory`.
- `python -m app.train` for bootstrap verification.
- `python -m pytest -q` for focused V1 unit verification.

## Trade-Offs
- Chose scaffolding-first to keep future chunks focused and verifiable.
- Kept schema validation lightweight (no external schema framework yet) to avoid premature complexity.
