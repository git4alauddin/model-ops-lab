# V2 Commit Log

This file records meaningful V2 commits and the operational purpose of each change.

## Pending - v2-c1: create validation foundation

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
