# V2 Verification

## Checks Performed
- Verified validation schema file loads successfully.
- Verified malformed schema contract raises a controlled validation error.
- Verified validation report status changes to failed for blocking issues.
- Verified validation readiness can load the current config, dataset, and schema together.
- Verified missing required columns are reported as `ERROR`.
- Verified unexpected dataframe columns are reported as `ERROR`.
- Verified structural validation failures make the readiness report status `failed`.
- Verified dtype mismatches are reported as `ERROR`.
- Verified datatype validation passes for the current sample churn dataset.
- Verified datatype validation failures make the readiness report status `failed`.
- Verified non-nullable column null values are reported as `ERROR`.
- Verified nullable columns can contain null values.
- Verified nullability validation failures make the readiness report status `failed`.
- Verified null percentage validation passes for the current sample churn dataset.
- Verified moderate nullable-column missingness is reported as `WARNING`.
- Verified high nullable-column missingness is reported as `ERROR`.
- Verified warning-only null percentage issues keep the validation report status `passed`.
- Verified error-level null percentage issues make the validation report status `failed`.
- Verified invalid null percentage schema thresholds are rejected safely.
- Verified numeric range violations are reported as `ERROR`.
- Verified below-minimum and above-maximum values are detected.
- Verified range validation failures make the readiness report status `failed`.
- Verified outlier sanity validation passes for the current sample churn dataset.
- Verified suspicious high numeric values are reported as `WARNING`.
- Verified suspicious low numeric values are reported as `WARNING`.
- Verified outlier sanity warnings keep the validation report status `passed`.
- Verified invalid outlier sanity schema thresholds are rejected safely.
- Verified allowed-value violations are reported as `ERROR`.
- Verified invalid categorical, boolean-like, and target values are detected.
- Verified allowed-value validation failures make the readiness report status `failed`.
- Verified duplicate rows are reported as `WARNING`.
- Verified duplicate IDs are reported as `ERROR`.
- Verified duplicate row warnings do not fail the report by themselves.
- Verified duplicate ID errors make the readiness report status `failed`.
- Verified validation report JSON persistence.
- Verified validation text summary persistence.
- Verified validation report paths are config-driven.
- Verified warning/error counts are written to the text summary.
- Verified training validation gate allows clean validation reports.
- Verified training validation gate allows warning-only validation reports.
- Verified training validation gate blocks failed validation reports.
- Verified training logs validation status and issue counts before training.
- Verified target distribution validation passes for the current sample churn dataset.
- Verified single-class target distributions are reported as `ERROR`.
- Verified heavily imbalanced target distributions are reported as `WARNING`.
- Verified warning-only target imbalance keeps the validation report status `passed`.
- Verified single-class target distribution makes the validation report status `failed`.
- Verified invalid target distribution schema thresholds are rejected safely.

## Commands Executed
- `python -m pytest -q`
- `python -m app.validate_data`

## Expected Output
- V1 tests continue passing.
- V2-C1 validation foundation tests pass.
- Validation command completes using `configs/training.yaml` and `schema_versions/customer_churn_v1.yaml`.
- Structural validation returns no issues for the current sample churn dataset.
- Datatype validation returns no issues for the current sample churn dataset.
- Nullability validation returns no issues for the current sample churn dataset.
- Null percentage validation returns no issues for the current sample churn dataset.
- Null percentage warnings remain non-blocking.
- Error-level null percentage failures are blocking.
- Numeric range validation returns no issues for the current sample churn dataset.
- Outlier sanity validation returns no issues for the current sample churn dataset.
- Outlier sanity warnings remain non-blocking.
- Allowed-value validation returns no issues for the current sample churn dataset.
- Duplicate validation returns no issues for the current sample churn dataset.
- Validation command generates ignored JSON and text report files.
- Training command runs validation before training.
- Target distribution validation returns no issues for the balanced sample churn dataset.
- Target distribution warnings remain non-blocking.
- Single-class target distribution failures are blocking.

## Actual Output
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `50 passed in 1.44s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully.
- Validation command returned `status='passed'`, `rows=20`, `columns=9`, `schema_version='v1'`, and no issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after moving shared dataset loading into `app/data.py`.
- After V2-C2 structural validation: `.\vir_env\Scripts\python.exe -m pytest -q` returned `54 passed in 2.79s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no structural issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after structural validation changes.
- After V2-C3 datatype validation: `.\vir_env\Scripts\python.exe -m pytest -q` returned `59 passed in 1.70s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no dtype issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after datatype validation changes.
- After V2-C4 nullability validation: `.\vir_env\Scripts\python.exe -m pytest -q` returned `63 passed in 1.81s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no nullability issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after nullability validation changes.
- After V2-C5 numeric range validation: `.\vir_env\Scripts\python.exe -m pytest -q` returned `68 passed in 3.03s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no range issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after range validation changes.
- After V2-C6 allowed-value validation: `.\vir_env\Scripts\python.exe -m pytest -q` returned `74 passed in 2.54s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no allowed-value issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after allowed-value validation changes.
- Initial V2-C7 duplicate validation test run returned `1 failed, 78 passed` because a duplicate row with `id_column` also correctly triggered duplicate ID failure.
- Adjusted the warning-only duplicate row test to omit `id_column`; duplicate ID failure remains covered separately.
- After V2-C7 duplicate validation: `.\vir_env\Scripts\python.exe -m pytest -q` returned `79 passed in 1.47s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no duplicate issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after duplicate validation changes.
- After V2-C8 validation report persistence: `.\vir_env\Scripts\python.exe -m pytest -q` returned `83 passed in 1.52s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully and generated `reports/validation_report.json` and `reports/validation_summary.txt`.
- Generated validation report files showed `status='passed'`, `rows=20`, `columns=9`, and `issues=[]`.
- Generated validation report files are ignored by git while `reports/.gitkeep` remains tracked.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after validation report persistence changes.
- After V2-C9 training validation gate: `.\vir_env\Scripts\python.exe -m pytest -q` returned `89 passed in 1.52s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully and generated validation reports.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and logged validation status before training.
- Training validation log showed `status=passed`, `issues=0`, `warnings=0`, `errors=0`, and `critical=0`.
- After V2-C10 target distribution validation: `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v2_c10_target_distribution_validation.py` returned `7 passed in 0.57s`.
- After V2-C10 target distribution validation: `.\vir_env\Scripts\python.exe -m pytest -q` returned `96 passed in 1.53s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and `issues=[]`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and logged validation status before training.
- Training validation log showed `status=passed`, `issues=0`, `warnings=0`, `errors=0`, and `critical=0`.
- After V2-C11 null percentage validation: `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v2_c11_null_percentage_validation.py` returned `8 passed in 0.50s`.
- After V2-C11 null percentage validation: `.\vir_env\Scripts\python.exe -m pytest -q` returned `104 passed in 1.58s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and `issues=[]`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and logged validation status before training.
- Training validation log showed `status=passed`, `issues=0`, `warnings=0`, `errors=0`, and `critical=0`.
- After V2-C12 outlier sanity validation: `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v2_c12_outlier_sanity_validation.py` returned `6 passed in 0.43s`.
- After V2-C12 outlier sanity validation: `.\vir_env\Scripts\python.exe -m pytest -q` returned `110 passed in 1.61s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and `issues=[]`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and logged validation status before training.
- Training validation log showed `status=passed`, `issues=0`, `warnings=0`, `errors=0`, and `critical=0`.

## Outcome
V2-C1 validation foundation is operational.
The validation command can load the current training config, sample dataset, and versioned schema together.
V2-C2 structural validation is operational.
V2-C3 datatype validation is operational.
V2-C4 nullability validation is operational.
V2-C5 numeric range validation is operational.
V2-C6 allowed-value validation is operational.
V2-C7 duplicate validation is operational.
V2-C8 validation report persistence is operational.
V2-C9 training validation gate is operational.
V2-C10 target distribution sanity checks are operational.
V2-C11 null percentage quality checks are operational.
V2-C12 outlier sanity checks are operational.
