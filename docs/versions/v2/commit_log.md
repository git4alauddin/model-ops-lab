# V2 Commit Log

This file records meaningful V2 commits and the operational purpose of each change.

## a2fd55d - v2-c1: create validation foundation

### What Changed
- Added `app/validate_data.py` as the V2 validation command entrypoint.
- Added `app/data.py` as a shared controlled CSV loading utility.
- Added `app/validation/` package.
- Added validation schema loading in `app/validation/checks.py`.
- Added validation report structures in `app/validation/reports.py`.
- Added first versioned churn dataset schema at `schema_versions/customer_churn_v1.yaml`.
- Added focused V2-C1 validation foundation tests.
- Added V2 documentation files under `docs/versions/v2/`.

### What Problem It Solved
- Creates a dedicated home for data validation before adding deeper checks.
- Makes the dataset contract explicit and version-controlled.
- Separates validation readiness from the V1 training pipeline.
- Avoids coupling validation command imports to the training entrypoint.
- Establishes the report shape that later validation checks can populate.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `50 passed in 1.44s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully.
- Validation command returned a passed readiness report with `rows=20`, `columns=9`, `schema_version='v1'`, and no issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after moving shared dataset loading into `app/data.py`.

## ce48590 - v2-c2: add structural schema validation

### What Changed
- Added required column validation in `app/validation/checks.py`.
- Added unexpected column validation in `app/validation/checks.py`.
- Added combined structural schema validation helper.
- Updated `app/validate_data.py` to include structural issues in the validation report.
- Updated README and V2 documentation.
- Added focused structural validation tests.

### What Problem It Solved
- Detects schema drift before dtype, null, range, or category checks run.
- Flags missing required fields as blocking validation issues.
- Flags unexpected dataframe columns as blocking validation issues.
- Makes validation reports reflect actual dataframe-vs-schema structure.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `54 passed in 2.79s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no structural issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after structural validation changes.

## 9a123c5 - v2-c3: add datatype validation

### What Changed
- Added column datatype validation in `app/validation/checks.py`.
- Added pandas dtype mapping for schema labels: `string`, `integer`, `float`, `boolean`, and `category`.
- Updated schema loading to reject unsupported schema dtype labels.
- Updated `app/validate_data.py` to include datatype issues in the validation report.
- Updated README and V2 documentation.
- Added focused datatype validation tests.

### What Problem It Solved
- Detects dataframe columns with the right names but wrong types.
- Blocks schema drift where numeric, boolean, or categorical fields arrive in an unexpected representation.
- Keeps validation reporting consistent by returning `ERROR` issues for dtype mismatches.
- Prepares the validation layer for null, range, and categorical value checks.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `59 passed in 1.70s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no dtype issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after datatype validation changes.

## c32f845 - v2-c4: add nullability validation

### What Changed
- Added nullable field validation in `app/validation/checks.py`.
- Added `validate_nullable_columns` using `nullable` rules from the versioned schema.
- Updated `app/validate_data.py` to include nullability issues in the validation report.
- Updated README and V2 documentation.
- Added focused nullability validation tests.

### What Problem It Solved
- Detects required fields that are present but not filled.
- Blocks datasets with null values in `nullable: false` columns.
- Keeps required-column presence separate from required-field completeness.
- Prepares validation for range and categorical value checks.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `63 passed in 1.81s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no nullability issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after nullability validation changes.

## Pending - v2-c5: add range validation

### What Changed
- Added numeric range validation in `app/validation/checks.py`.
- Added `validate_numeric_ranges` using `min` and `max` rules from the versioned schema.
- Added schema validation for numeric range bounds.
- Updated `app/validate_data.py` to include range issues in the validation report.
- Updated README and V2 documentation.
- Added focused range validation tests.

### What Problem It Solved
- Detects impossible or unrealistic numeric values before training.
- Blocks values below schema minimums or above schema maximums.
- Keeps range failures separate from dtype and nullability failures.
- Prepares validation for categorical allowed-value checks.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `68 passed in 3.03s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no range issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after range validation changes.
