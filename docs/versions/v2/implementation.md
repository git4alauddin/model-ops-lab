# V2 Implementation

## Scope
Chunk V2-C1: validation foundation.

## V2-C1 Additions
- `app/validate_data.py`
  - added command entrypoint for validation readiness
  - loads training config
  - loads current dataset
  - loads versioned validation schema
  - returns initial validation report
  - logs validation scaffold outcome
- `app/data.py`
  - moved shared controlled CSV loading out of the training entrypoint
  - allows training and validation to reuse the same dataset loading behavior
- `app/validation/checks.py`
  - added `ValidationError`
  - added `load_validation_schema`
  - validates schema metadata and column rule contract
- `app/validation/reports.py`
  - added `ValidationIssue`
  - added `ValidationReport`
  - added status derivation from issue severity
- `schema_versions/customer_churn_v1.yaml`
  - added first versioned schema for `data/churn.csv`
  - defines expected columns, dtypes, nullable rules, roles, ranges, and allowed values
- `tests/test_v2_c1_validation_foundation.py`
  - validates schema loading
  - validates malformed schema failure
  - validates report status behavior
  - validates dataset/schema readiness path

## Current V2-C1 Workflow
```text
configs/training.yaml
  -> resolve dataset path
  -> load data/churn.csv through shared dataset loader
  -> load schema_versions/customer_churn_v1.yaml
  -> verify schema file contract
  -> build initial validation readiness report
  -> log validation scaffold result
```

## Not Yet Implemented
- required column validation against the dataframe
- unexpected column detection
- dataframe dtype validation
- nullable field validation
- range and categorical checks
- duplicate checks
- persisted validation reports
- training pipeline integration
