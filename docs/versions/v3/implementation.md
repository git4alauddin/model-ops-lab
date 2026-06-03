# V3 Implementation

## Scope
Chunk V3-C1: dataset registry foundation.
Chunk V3-C2: record dataset version in training metadata.
Chunk V3-C3: record dataset version in validation reports.
Chunk V3-C4: add dataset checksum tracking.

## V3-C1 Additions
- `data_versions/customer_churn/v1.yaml`
  - records the first explicit dataset version
  - links the dataset version to `data/churn.csv`
  - links the dataset version to `schema_versions/customer_churn_v1.yaml`
  - records target column, ID column, source type, owner, and status
- `app/dataset_registry.py`
  - added `DatasetRegistryError`
  - added required dataset version metadata keys
  - added controlled YAML metadata loading
  - added metadata contract validation
- `tests/test_v3_c1_dataset_registry.py`
  - validates successful registry metadata loading
  - validates missing metadata file failure
  - validates invalid YAML failure
  - validates required key enforcement
  - validates required value type enforcement
- `docs/versions/v3/`
  - added V3 overview, implementation notes, verification notes, lessons, issues, and commit log
- `README.md`
  - added V3 status
  - added `data_versions/` to the project structure

## Current V3-C1 Workflow
```text
data_versions/customer_churn/v1.yaml
  -> load through app.dataset_registry
  -> validate required metadata keys
  -> return dataset version metadata for later training and validation integration
```

## V3-C2 Additions
- `configs/training.yaml`
  - added `dataset_version.metadata_path`
  - points training to `data_versions/customer_churn/v1.yaml`
- `app/train.py`
  - added dataset version metadata path resolution
  - loads dataset version metadata during training
  - builds a stable dataset version snapshot for training metadata
  - writes the snapshot into `artifacts/training_metadata.json`
  - logs the active dataset version in a readable `[DATASET VERSION]` section
- `tests/test_v3_c2_training_dataset_version.py`
  - validates configured dataset version metadata path resolution
  - validates default dataset version metadata path resolution
  - validates training metadata snapshot fields
  - validates configured missing metadata files fail safely
- `docs/versions/v3/`
  - updated implementation, verification, lessons, issues, and commit log for V3-C2
- `README.md`
  - updated V3 status and default config notes

## Current V3-C2 Workflow
```text
configs/training.yaml
  -> read dataset_version.metadata_path
  -> load data_versions/customer_churn/v1.yaml
  -> build dataset_version snapshot
  -> run validation gate
  -> train baseline model
  -> persist dataset_version inside artifacts/training_metadata.json
  -> log active dataset version
```

## V3-C3 Additions
- `app/validation/reports.py`
  - added optional `dataset_version` field to `ValidationReport`
  - persists dataset version snapshots in JSON validation reports
  - includes dataset version details in text validation summaries
- `app/validate_data.py`
  - loads dataset version metadata during validation
  - adds dataset version snapshot to readiness reports
  - logs active dataset version in a readable `[DATASET VERSION]` section
- `tests/test_v3_c3_validation_dataset_version.py`
  - validates validation report dataset version snapshots
  - validates JSON report dataset version persistence
  - validates text summary dataset version output
  - validates readiness reports populate dataset version metadata
- `docs/versions/v3/`
  - updated implementation, verification, lessons, issues, and commit log for V3-C3
- `README.md`
  - updated V3 status

## Current V3-C3 Workflow
```text
python -m app.validate_data
  -> read dataset_version.metadata_path
  -> load data_versions/customer_churn/v1.yaml
  -> run validation checks
  -> persist dataset_version inside reports/validation_report.json
  -> write dataset_version inside reports/validation_summary.txt
  -> log active dataset version
```

## V3-C4 Additions
- `data_versions/customer_churn/v1.yaml`
  - added SHA256 checksum metadata for `data/churn.csv`
- `app/dataset_registry.py`
  - added `calculate_file_checksum`
  - added `validate_dataset_checksum`
  - added checksum metadata to runtime dataset version snapshots
  - exposes checksum metadata in training logs, validation logs, and validation summaries
  - rejects unsupported checksum algorithms
  - rejects missing dataset files during checksum validation
  - rejects checksum mismatches safely
- `tests/test_v3_c4_dataset_checksum.py`
  - validates deterministic SHA256 calculation
  - validates current dataset checksum metadata
  - validates checksum mismatch failure
  - validates missing dataset file failure
  - validates unsupported checksum algorithm failure
- `tests/test_v3_c2_training_dataset_version.py`
  - validates training metadata snapshots include checksum metadata
- `tests/test_v3_c3_validation_dataset_version.py`
  - validates validation report snapshots include checksum metadata
- `docs/versions/v3/`
  - updated implementation, verification, lessons, issues, and commit log for V3-C4
- `README.md`
  - updated V3 status

## Current V3-C4 Workflow
```text
Get-FileHash data\churn.csv -Algorithm SHA256
  -> record hash in data_versions/customer_churn/v1.yaml
  -> load dataset version metadata
  -> calculate dataset file checksum when checksum validation is requested
  -> compare actual checksum with registry checksum
  -> include checksum metadata in training and validation snapshots
```

## Remaining V3 Gaps
- No reproducibility check command exists yet.
