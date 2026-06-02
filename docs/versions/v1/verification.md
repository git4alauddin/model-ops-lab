# V1 Verification

## Checks Performed
- Confirmed required folders were created.
- Confirmed required scaffold files were created.
- Ran training bootstrap to verify controlled failure handling.
- Ran unit tests for config validation, dataset loading, and feature-target split.
- Ran unit tests for train-test split behavior and reproducibility.
- Ran unit tests for feature type detection.
- Ran unit tests for preprocessing pipeline construction and unknown-category handling.
- Ran unit tests for baseline model construction, training pipeline composition, and controlled training failure.
- Ran unit tests and training bootstrap against the synthetic churn smoke dataset.

## Commands Executed
- `Get-ChildItem -Recurse -File app,configs,docs,data,artifacts`
- `git status --short`
- `python -m app.train`
- `python -m pytest -q`

## Expected Output
- Training bootstrap starts.
- If dataset is missing, process exits with controlled `Dataset file not found` error.
- With `data/churn.csv` present, training bootstrap completes successfully.

## Actual Output
- `INFO Training bootstrap started`
- `ERROR Training bootstrap failed: Dataset file not found: data\churn.csv`
- Process exited with status code `1`.
- Initial test run failed with: `No module named pytest` (interpreter mismatch).
- After selecting the correct interpreter and installing dependencies: `6 passed in 0.38s`.
- After adding feature-target split tests: `9 passed in 1.07s`.
- After adding train-test split tests: `13 passed in 2.55s`.
- After adding feature type detection tests: `18 passed in 1.34s`.
- After adding preprocessing pipeline tests: `23 passed in 1.32s`.
- After renaming tests to component-aware filenames: `23 passed in 1.31s`.
- After adding baseline model training tests: `28 passed in 1.36s`.
- After cleaning `train.py` IDE inspection issues: `28 passed in 1.27s`.
- After adding sample churn dataset smoke tests: `31 passed in 1.32s`.
- `python -m app.train` completed successfully with `rows=20`, `train_rows=16`, `test_rows=4`, `numeric_features=3`, `categorical_features=4`, and `fitted_steps=2`.

## Outcome
Scaffold, V1-C2 error handling path, V1-C3 feature-target split, V1-C4 train-test split, V1-C5 feature type detection, V1-C6 preprocessing pipeline construction, V1-C7 baseline model training, and V1-C8 sample dataset smoke run are operational.
Unit tests are passing in the project virtual environment.
