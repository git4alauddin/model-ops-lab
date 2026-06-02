# V2 Implementation

## Scope
Chunk V2-C1: validation foundation.
Chunk V2-C2: structural schema validation.
Chunk V2-C3: datatype validation.
Chunk V2-C4: nullability validation.
Chunk V2-C5: numeric range validation.
Chunk V2-C6: allowed-value validation.

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

## V2-C4 Additions
- `app/validation/checks.py`
  - added `validate_nullable_columns`
  - reads `nullable` rules from the versioned schema
  - skips missing columns so structural validation remains the source for missing-column issues
  - emits `ERROR` issues when `nullable: false` columns contain null values
- `app/validate_data.py`
  - runs nullability checks after structural and dtype checks
  - includes nullability failures in the validation report
- `tests/test_v2_c4_nullability_validation.py`
  - validates current churn dataset nullability success
  - validates non-nullable column failure
  - validates nullable columns can contain null values
  - validates failed readiness report for nullability violations
- `README.md`
  - updated V2 status with nullability validation

## Current V2-C4 Workflow
```text
configs/training.yaml
  -> resolve dataset path
  -> load data/churn.csv
  -> load schema_versions/customer_churn_v1.yaml
  -> compare dataframe columns with schema columns
  -> compare present dataframe dtypes with schema dtype rules
  -> check nullable:false columns for null values
  -> add ERROR issue for nullability violations
  -> build validation report with passed/failed status
  -> log validation result
```

## V2-C5 Additions
- `app/validation/checks.py`
  - added `validate_numeric_ranges`
  - reads `min` and `max` rules from the versioned schema
  - skips missing, null-only, and non-numeric columns
  - emits `ERROR` issues when numeric values fall below `min` or above `max`
  - validates schema numeric bounds during schema loading
- `app/validate_data.py`
  - runs numeric range checks after structural, dtype, and nullability checks
  - includes range failures in the validation report
- `tests/test_v2_c5_range_validation.py`
  - validates current churn dataset range success
  - validates below-minimum failures
  - validates above-maximum failures
  - validates negative charge failures
  - validates failed readiness report for range violations
- `README.md`
  - updated V2 status with numeric range validation

## Current V2-C5 Workflow
```text
configs/training.yaml
  -> resolve dataset path
  -> load data/churn.csv
  -> load schema_versions/customer_churn_v1.yaml
  -> compare dataframe columns with schema columns
  -> compare present dataframe dtypes with schema dtype rules
  -> check nullable:false columns for null values
  -> check numeric columns against min/max bounds
  -> add ERROR issue for range violations
  -> build validation report with passed/failed status
  -> log validation result
```

## V2-C6 Additions
- `app/validation/checks.py`
  - added `validate_allowed_values`
  - reads `allowed_values` lists from the versioned schema
  - skips missing and null values so structural and nullability checks own those failures
  - emits `ERROR` issues when observed values are outside the allowed set
  - validates `allowed_values` schema rules during schema loading
- `app/validate_data.py`
  - runs allowed-value checks after range checks
  - includes categorical, boolean, and controlled-target value failures in the validation report
- `tests/test_v2_c6_allowed_values_validation.py`
  - validates current churn dataset allowed-value success
  - validates invalid contract type failure
  - validates invalid internet service failure
  - validates invalid target value failure
  - validates invalid boolean-like value failure
  - validates failed readiness report for invalid allowed values
- `README.md`
  - updated V2 status with allowed-value validation

## Current V2-C6 Workflow
```text
configs/training.yaml
  -> resolve dataset path
  -> load data/churn.csv
  -> load schema_versions/customer_churn_v1.yaml
  -> compare dataframe columns with schema columns
  -> compare present dataframe dtypes with schema dtype rules
  -> check nullable:false columns for null values
  -> check numeric columns against min/max bounds
  -> check controlled columns against allowed_values
  -> add ERROR issue for invalid observed values
  -> build validation report with passed/failed status
  -> log validation result
```

## Not Yet Implemented
- duplicate checks
- persisted validation reports
- training pipeline integration
