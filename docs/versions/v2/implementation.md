# V2 Implementation

## Scope
Chunk V2-C1: validation foundation.
Chunk V2-C2: structural schema validation.
Chunk V2-C3: datatype validation.
Chunk V2-C4: nullability validation.
Chunk V2-C5: numeric range validation.
Chunk V2-C6: allowed-value validation.
Chunk V2-C7: duplicate validation.
Chunk V2-C8: validation report persistence.
Chunk V2-C9: training validation gate.
Chunk V2-C10: target distribution sanity checks.
Chunk V2-C11: null percentage quality checks.

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

## V2-C7 Additions
- `app/validation/checks.py`
  - added `validate_duplicate_rows`
  - added `validate_duplicate_ids`
  - duplicate rows produce `WARNING`
  - duplicate IDs produce `ERROR` using schema `id_column`
  - validates schema `id_column` type during schema loading
- `app/validate_data.py`
  - runs duplicate checks after allowed-value checks
  - includes duplicate row warnings and duplicate ID errors in the validation report
- `tests/test_v2_c7_duplicate_validation.py`
  - validates current churn dataset duplicate success
  - validates duplicate row warning behavior
  - validates duplicate ID error behavior
  - validates passed readiness report for duplicate row warning only
  - validates failed readiness report for duplicate IDs
- `README.md`
  - updated V2 status with duplicate validation

## Current V2-C7 Workflow
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
  -> check duplicate rows
  -> check duplicate id_column values
  -> build validation report with passed/failed status
  -> log validation result
```

## V2-C8 Additions
- `app/validation/reports.py`
  - added `ValidationReportError`
  - added `build_report_paths`
  - added `save_validation_report`
  - added `build_validation_summary`
  - added `save_validation_summary`
  - summarizes total issues and severity counts
- `configs/training.yaml`
  - added config-driven validation report paths
- `app/validate_data.py`
  - persists `reports/validation_report.json`
  - persists `reports/validation_summary.txt`
  - logs generated report paths
- `.gitignore`
  - ignores generated validation report files
  - keeps `reports/.gitkeep` tracked
- `tests/test_v2_c8_validation_report_persistence.py`
  - validates config-driven report paths
  - validates JSON report persistence
  - validates text summary persistence
  - validates warning/error counts in the summary
- `README.md`
  - documents generated validation reports as ignored runtime outputs

## Current V2-C8 Workflow
```text
python -m app.validate_data
  -> run validation checks
  -> build validation report object
  -> save reports/validation_report.json
  -> save reports/validation_summary.txt
  -> log validation report paths
```

## V2-C9 Additions
- `configs/training.yaml`
  - added `validation.schema_path`
- `app/train.py`
  - added `ValidationGateError`
  - added `resolve_validation_schema_path`
  - added `count_validation_issues`
  - added `enforce_validation_gate`
  - runs validation before dataset preprocessing and model training
  - logs validation status and issue counts
  - blocks training when validation report status is `failed`
  - allows training to continue for warning-only validation reports
- `tests/test_v2_c9_training_validation_gate.py`
  - validates clean reports pass the gate
  - validates warning-only reports pass the gate
  - validates failed reports block training
  - validates validation issue counts
  - validates configured/default schema path resolution
- `README.md`
  - updated V2 status with training validation gate

## Current V2-C9 Workflow
```text
python -m app.train
  -> load configs/training.yaml
  -> resolve validation.schema_path
  -> run validation checks
  -> log validation status and issue counts
  -> if validation status is failed: stop training
  -> if validation status is passed: continue training
```

## V2-C10 Additions
- `schema_versions/customer_churn_v1.yaml`
  - added `quality_checks.target_distribution`
  - added schema-driven `min_class_ratio` and `max_class_ratio` thresholds
  - keeps target distribution rules versioned with the dataset contract
- `app/validation/checks.py`
  - added `validate_target_distribution`
  - returns `ERROR` when the target has no non-null values
  - returns `ERROR` when the target contains only one class
  - returns `WARNING` when class distribution violates configured ratio thresholds
  - validates target distribution threshold configuration during schema loading
- `app/validate_data.py`
  - runs target distribution validation after duplicate checks
  - includes target distribution issues in the validation report
- `tests/test_v2_c10_target_distribution_validation.py`
  - validates clean sample churn distribution
  - validates single-class target failure
  - validates imbalanced target warning
  - validates disabled target distribution checks
  - validates invalid target distribution schema thresholds
  - validates readiness reports for target distribution warnings and errors
- `README.md`
  - updated V2 status with target distribution sanity checks

## Current V2-C10 Workflow
```text
python -m app.validate_data
  -> run schema, dtype, nullability, range, allowed-value, and duplicate checks
  -> inspect configured target column distribution
  -> return ERROR for unusable single-class targets
  -> return WARNING for suspicious target imbalance
  -> include target distribution issues in persisted validation reports

python -m app.train
  -> run validation first
  -> block training when target distribution validation fails
  -> continue training when target distribution only warns
```

## V2-C11 Additions
- `schema_versions/customer_churn_v1.yaml`
  - added `quality_checks.null_percentages`
  - added schema-driven default warning and error thresholds
  - keeps missingness rules versioned with the dataset contract
- `app/validation/checks.py`
  - added `validate_null_percentages`
  - returns `WARNING` when nullable column null ratio exceeds the warning threshold
  - returns `ERROR` when nullable column null ratio exceeds the error threshold
  - skips non-nullable columns unless a column override is explicitly configured
  - validates null percentage threshold configuration during schema loading
- `app/validate_data.py`
  - runs null percentage validation after strict nullability checks
  - includes null percentage issues in validation reports
- `tests/test_v2_c11_null_percentage_validation.py`
  - validates clean sample churn missingness
  - validates warning-level missingness
  - validates error-level missingness
  - validates disabled null percentage checks
  - validates invalid null percentage schema thresholds
  - validates readiness reports for null percentage warnings and errors
- `README.md`
  - updated V2 status with null percentage checks

## Current V2-C11 Workflow
```text
python -m app.validate_data
  -> run schema, dtype, and strict nullability checks
  -> inspect nullable column null percentages
  -> return WARNING for suspicious missingness
  -> return ERROR for unsafe missingness
  -> continue remaining quality checks
  -> include null percentage issues in persisted validation reports

python -m app.train
  -> run validation first
  -> block training when null percentage validation fails
  -> continue training when null percentage validation only warns
```

## Not Yet Implemented
- outlier sanity checks
- validation duration and metadata persistence
- final V2 closure documentation
