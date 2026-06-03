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

## ce7a840 - v2-c5: add range validation

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

## 82bac44 - v2-c6: add allowed-value validation

### What Changed
- Added allowed-value validation in `app/validation/checks.py`.
- Added `validate_allowed_values` using `allowed_values` rules from the versioned schema.
- Added schema validation for `allowed_values` rules.
- Updated `app/validate_data.py` to include allowed-value issues in the validation report.
- Updated README and V2 documentation.
- Added focused allowed-value validation tests.

### What Problem It Solved
- Detects invalid categorical values before training.
- Detects controlled target values outside the expected set.
- Detects invalid boolean-like values for schema-controlled boolean fields.
- Keeps categorical constraints explicit and version-controlled.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `74 passed in 2.54s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no allowed-value issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after allowed-value validation changes.

## 1b67cf7 - v2-c7: add duplicate validation

### What Changed
- Added duplicate row validation in `app/validation/checks.py`.
- Added duplicate ID validation using schema `id_column`.
- Added `WARNING` severity for duplicate rows.
- Added `ERROR` severity for duplicate IDs.
- Updated `app/validate_data.py` to include duplicate issues in the validation report.
- Updated README and V2 documentation.
- Added focused duplicate validation tests.

### What Problem It Solved
- Detects repeated records before training.
- Detects broken customer identity uniqueness before training.
- Uses severity levels to distinguish suspicious duplicates from blocking identity errors.
- Moves V2 closer to a practical data quality gate.

### Verification
- Initial `.\vir_env\Scripts\python.exe -m pytest -q` returned `1 failed, 78 passed` because a duplicate row with `id_column` also correctly triggered duplicate ID failure.
- Adjusted the warning-only duplicate row test to omit `id_column`; duplicate ID failure remains covered separately.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `79 passed in 1.47s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no duplicate issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after duplicate validation changes.

## cb7f8af - v2-c8: persist validation reports

### What Changed
- Added validation report path construction in `app/validation/reports.py`.
- Added validation report JSON persistence.
- Added validation summary text persistence.
- Added validation report persistence errors.
- Added validation report output config in `configs/training.yaml`.
- Updated `app/validate_data.py` to persist JSON and text validation reports.
- Added `reports/.gitkeep`.
- Updated `.gitignore` to ignore generated validation reports.
- Updated README and V2 documentation.
- Added focused validation report persistence tests.

### What Problem It Solved
- Makes validation results inspectable after the command finishes.
- Provides structured JSON output for automation.
- Provides readable text output for quick local review.
- Keeps generated validation outputs out of git while preserving the report folder.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `83 passed in 1.52s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully and generated `reports/validation_report.json` and `reports/validation_summary.txt`.
- Generated validation report files showed `status='passed'`, `rows=20`, `columns=9`, and `issues=[]`.
- Generated validation report files are ignored by git while `reports/.gitkeep` remains tracked.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after validation report persistence changes.

## 88dd34c - v2-c9: integrate validation gate into training

### What Changed
- Added `validation.schema_path` to `configs/training.yaml`.
- Added `ValidationGateError` in `app/train.py`.
- Added validation schema path resolution in `app/train.py`.
- Added validation issue counting in `app/train.py`.
- Added training validation gate enforcement in `app/train.py`.
- Updated training flow to run validation before dataset preprocessing and model training.
- Updated training logs with validation status and issue counts.
- Updated README and V2 documentation.
- Added focused training validation gate tests.

### What Problem It Solved
- Turns validation from a separate command into a training safety gate.
- Stops training before preprocessing or fitting when validation reports blocking issues.
- Keeps warning-only validation reports visible without blocking training.
- Makes the V2 validation layer operationally relevant to the training pipeline.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `89 passed in 1.52s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully and generated validation reports.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and logged validation status before training.
- Training validation log showed `status=passed`, `issues=0`, `warnings=0`, `errors=0`, and `critical=0`.

## fb5c5a6 - v2-c10: add target distribution sanity checks

### What Changed
- Added `quality_checks.target_distribution` to `schema_versions/customer_churn_v1.yaml`.
- Added `validate_target_distribution` in `app/validation/checks.py`.
- Added schema validation for target distribution threshold configuration.
- Updated `app/validate_data.py` to include target distribution checks in readiness reports.
- Added focused target distribution validation tests.
- Updated README and V2 documentation.
- Corrected the V2-C9 commit log entry from `Pending` to `88dd34c`.

### What Problem It Solved
- Detects target columns that are structurally valid but unusable for classifier training.
- Blocks single-class targets before preprocessing or model fitting.
- Warns on heavily imbalanced target distributions without blocking training by default.
- Keeps target quality thresholds versioned with the dataset schema.

### Verification
- Initial focused V2-C10 test run returned `2 failed, 5 passed` because the one-column readiness fixtures also triggered existing duplicate-row warnings.
- Updated readiness fixtures to include unique `customer_id` values so the tests isolate target distribution behavior.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v2_c10_target_distribution_validation.py` returned `7 passed in 0.57s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `96 passed in 1.53s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no validation issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and logged validation status before training.

## 14980d2 - v2-c11: add null percentage quality checks

### What Changed
- Added `quality_checks.null_percentages` to `schema_versions/customer_churn_v1.yaml`.
- Added `validate_null_percentages` in `app/validation/checks.py`.
- Added schema validation for null percentage threshold configuration.
- Updated `app/validate_data.py` to include null percentage checks in readiness reports.
- Added focused null percentage validation tests.
- Updated README and V2 documentation.

### What Problem It Solved
- Detects nullable columns with operationally unsafe missingness.
- Keeps strict non-nullability failures separate from percentage-based data quality failures.
- Allows warning-level missingness to stay visible without blocking training.
- Blocks training when missingness crosses configured error thresholds.
- Keeps missingness thresholds versioned with the dataset schema.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v2_c11_null_percentage_validation.py` returned `8 passed in 0.50s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `104 passed in 1.58s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no validation issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and logged validation status before training.

## Pending - v2-c12: add outlier sanity checks

### What Changed
- Added `quality_checks.outlier_sanity` to `schema_versions/customer_churn_v1.yaml`.
- Added `validate_outlier_sanity` in `app/validation/checks.py`.
- Added schema validation for outlier sanity threshold configuration.
- Updated `app/validate_data.py` to include outlier sanity checks in readiness reports.
- Added focused outlier sanity validation tests.
- Updated README and V2 documentation.
- Corrected the V2-C11 commit log entry from `Pending` to `14980d2`.

### What Problem It Solved
- Detects numeric values that are technically valid but operationally suspicious.
- Keeps hard numeric range failures separate from warning-level outlier signals.
- Makes suspicious numeric spikes visible before model training.
- Keeps outlier sanity thresholds versioned with the dataset schema.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v2_c12_outlier_sanity_validation.py` returned `6 passed in 0.43s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `110 passed in 1.61s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status='passed'`, `rows=20`, `columns=9`, and no validation issues.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully and logged validation status before training.
