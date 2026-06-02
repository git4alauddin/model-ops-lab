# V2 Implementation

## Scope
Chunk V2-C1: validation foundation.
Chunk V2-C2: structural schema validation.
Chunk V2-C3: datatype validation.

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

## V2-C2 Additions
- `app/validation/checks.py`
  - added `validate_required_columns`
  - added `validate_unexpected_columns`
  - added `validate_schema_columns`
  - returns `ValidationIssue` objects for structural failures
- `app/validate_data.py`
  - runs structural dataframe-vs-schema checks after loading data and schema
  - includes structural issues in the validation report
  - report status becomes `failed` when missing or unexpected columns exist
- `tests/test_v2_c2_structural_validation.py`
  - validates missing required column detection
  - validates unexpected column detection
  - validates matching structure success
  - validates failed readiness report for bad dataset structure
- `README.md`
  - updated V2 status with structural column validation

## Current V2-C2 Workflow
```text
configs/training.yaml
  -> resolve dataset path
  -> load data/churn.csv
  -> load schema_versions/customer_churn_v1.yaml
  -> compare dataframe columns with schema columns
  -> add ERROR issue for missing required columns
  -> add ERROR issue for unexpected columns
  -> build validation report with passed/failed status
  -> log validation result
```

## V2-C3 Additions
- `app/validation/checks.py`
  - added `validate_column_dtypes`
  - maps schema dtype labels to pandas-compatible checks
  - supports `string`, `integer`, `float`, `boolean`, and `category`
  - skips missing columns so structural validation remains the source for missing-column issues
  - rejects unsupported schema dtype labels during schema loading
- `app/validate_data.py`
  - runs datatype checks after structural checks
  - includes datatype failures in the validation report
- `tests/test_v2_c3_datatype_validation.py`
  - validates current churn dataset dtype success
  - validates wrong integer dtype failure
  - validates wrong float dtype failure
  - validates wrong boolean/category dtype failures
  - validates failed readiness report for wrong dtype
- `README.md`
  - updated V2 status with datatype validation

## Current V2-C3 Workflow
```text
configs/training.yaml
  -> resolve dataset path
  -> load data/churn.csv
  -> load schema_versions/customer_churn_v1.yaml
  -> compare dataframe columns with schema columns
  -> compare present dataframe dtypes with schema dtype rules
  -> add ERROR issue for dtype mismatches
  -> build validation report with passed/failed status
  -> log validation result
```

## Not Yet Implemented
- nullable field validation
- range and categorical checks
- duplicate checks
- persisted validation reports
- training pipeline integration
