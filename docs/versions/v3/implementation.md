# V3 Implementation

## Scope
Chunk V3-C1: dataset registry foundation.

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

## Remaining V3 Gaps
- Training metadata does not yet record dataset version.
- Validation reports do not yet record dataset version.
- Dataset checksums are not yet tracked.
- No reproducibility check command exists yet.
