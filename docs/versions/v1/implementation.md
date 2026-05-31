# V1 Implementation

## Scope
Chunk V1-C1: project scaffolding only.
Chunk V1-C2: config validation and robust dataset loading.

## Folder Structure
Established `app/`, `configs/`, `data/`, `artifacts/`, and documentation hierarchy under `docs/`.

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

## Configs Used
- `configs/training.yaml` created with placeholder baseline settings.

## Commands Used
- directory creation with PowerShell `New-Item -ItemType Directory`.
- `python -m app.train` for bootstrap verification.

## Trade-Offs
- Chose scaffolding-first to keep future chunks focused and verifiable.
- Kept schema validation lightweight (no external schema framework yet) to avoid premature complexity.
