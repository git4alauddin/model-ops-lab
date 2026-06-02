# V2 Verification

## Checks Performed
- Verified validation schema file loads successfully.
- Verified malformed schema contract raises a controlled validation error.
- Verified validation report status changes to failed for blocking issues.
- Verified validation readiness can load the current config, dataset, and schema together.
- Verified missing required columns are reported as `ERROR`.
- Verified unexpected dataframe columns are reported as `ERROR`.
- Verified structural validation failures make the readiness report status `failed`.

## Commands Executed
- `python -m pytest -q`
- `python -m app.validate_data`

## Expected Output
- V1 tests continue passing.
- V2-C1 validation foundation tests pass.
- Validation command completes using `configs/training.yaml` and `schema_versions/customer_churn_v1.yaml`.
- Structural validation returns no issues for the current sample churn dataset.

## Actual Output
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `50 passed in 1.44s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully.
- Validation command returned `status='passed'`, `rows=20`, `columns=9`, `schema_version='v1'`, and no issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after moving shared dataset loading into `app/data.py`.
- After V2-C2 structural validation: `.\vir_env\Scripts\python.exe -m pytest -q` returned `54 passed in 2.79s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no structural issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after structural validation changes.

## Outcome
V2-C1 validation foundation is operational.
The validation command can load the current training config, sample dataset, and versioned schema together.
V2-C2 structural validation is operational.
