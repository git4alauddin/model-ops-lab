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

## Pending - v2-c2: add structural schema validation

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
