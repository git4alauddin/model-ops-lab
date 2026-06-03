# V3 Commit Log

This file records meaningful V3 commits and the operational purpose of each change.

## 8dea077 - v3-c1: add dataset registry foundation

### What Changed
- Added the first dataset version registry entry for customer churn.
- Added dataset registry metadata loading and validation.
- Added focused V3-C1 dataset registry tests.
- Added V3 documentation files.
- Updated README with V3 status and structure.
- Corrected the V2-C14 commit log entry from `Pending` to `8cd63b4`.

### What Problem It Solved
- Makes the current dataset version explicit and inspectable.
- Creates a stable metadata contract before adding checksums and reproducibility enforcement.
- Gives later training and validation chunks a reusable dataset version metadata loader.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v3_c1_dataset_registry.py` returned `5 passed in 0.11s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `122 passed in 2.82s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status=passed`, `issues=0`, `warnings=0`, `errors=0`, and `critical=0`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after the validation gate passed.

## c3753cd - v3-c2: record dataset version in training metadata

### What Changed
- Added `dataset_version.metadata_path` to `configs/training.yaml`.
- Updated training to load dataset version metadata.
- Added a dataset version snapshot to generated training metadata.
- Added a readable `[DATASET VERSION]` training log section.
- Added focused V3-C2 training dataset version tests.
- Updated README and V3 documentation.
- Corrected the V3-C1 commit log entry from `Pending` to `8dea077`.

### What Problem It Solved
- Makes trained model artifacts traceable to a specific dataset registry entry.
- Connects the V3 dataset registry to a real runtime output.
- Keeps dataset version information inspectable in generated local metadata.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v3_c2_training_dataset_version.py` returned `4 passed in 1.26s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `126 passed in 1.77s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status=passed`, `issues=0`, `warnings=0`, `errors=0`, and `critical=0`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after the validation gate passed.
- Generated `artifacts/training_metadata.json` includes the `dataset_version` snapshot for `customer_churn` version `v1`.

## e6cbcd4 - v3-c3: record dataset version in validation reports

### What Changed
- Added dataset version snapshots to validation reports.
- Persisted dataset version metadata in `reports/validation_report.json`.
- Included dataset version metadata in `reports/validation_summary.txt`.
- Added a readable `[DATASET VERSION]` validation log section.
- Added focused V3-C3 validation dataset version tests.
- Updated README and V3 documentation.
- Corrected the V3-C2 commit log entry from `Pending` to `c3753cd`.

### What Problem It Solved
- Makes validation outputs traceable to the exact dataset registry entry they checked.
- Aligns validation report traceability with training metadata traceability.
- Prepares V3 for checksum and reproducibility checks.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v3_c2_training_dataset_version.py` returned `4 passed in 0.05s`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v3_c3_validation_dataset_version.py` returned `4 passed in 0.47s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `130 passed in 3.22s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status=passed`, `issues=0`, `warnings=0`, `errors=0`, and `critical=0`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after the validation gate passed.
- Generated `reports/validation_report.json` includes the `dataset_version` snapshot for `customer_churn` version `v1`.
- Generated `reports/validation_summary.txt` includes the dataset version section.

## 12aacfa - v3-c4: add dataset checksum tracking

### What Changed
- Added SHA256 checksum metadata to `data_versions/customer_churn/v1.yaml`.
- Added dataset checksum calculation in `app/dataset_registry.py`.
- Added dataset checksum validation in `app/dataset_registry.py`.
- Added checksum metadata to dataset version runtime snapshots.
- Exposed checksum metadata in training logs, validation logs, and validation summaries.
- Added focused V3-C4 checksum tests.
- Updated V3-C2 and V3-C3 tests to assert checksum metadata is carried forward.
- Updated README and V3 documentation.
- Corrected the V3-C3 commit log entry from `Pending` to `e6cbcd4`.

### What Problem It Solved
- Makes dataset content identity explicit, not only dataset version name.
- Detects when `data/churn.csv` no longer matches the registry metadata.
- Prepares V3 for a reproducibility check command.

### Verification
- `Get-FileHash data\churn.csv -Algorithm SHA256` returned `5F4F99466D4EF2703BE65C8597A6BD0D784EAAF83960690BDAC118FF3CFAE623`.
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v3_c2_training_dataset_version.py tests\test_v3_c3_validation_dataset_version.py tests\test_v3_c4_dataset_checksum.py` returned `13 passed in 0.49s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `135 passed in 2.27s`.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status=passed`, `issues=0`, `warnings=0`, `errors=0`, and `critical=0`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after the validation gate passed.
- Generated `artifacts/training_metadata.json` includes checksum algorithm `sha256` and checksum value `5f4f99466d4ef2703be65c8597a6bd0d784eaaf83960690bdac118ff3cfae623`.
- Generated `reports/validation_report.json` includes checksum algorithm `sha256` and checksum value `5f4f99466d4ef2703be65c8597a6bd0d784eaaf83960690bdac118ff3cfae623`.
- Generated `reports/validation_summary.txt` includes checksum algorithm `sha256` and checksum value `5f4f99466d4ef2703be65c8597a6bd0d784eaaf83960690bdac118ff3cfae623`.

## 25f7c13 - v3-c5: add reproducibility check command

### What Changed
- Added `app/check_reproducibility.py`.
- Added `ReproducibilityResult`.
- Added `check_reproducibility`.
- Added readable reproducibility command logs.
- Added focused V3-C5 reproducibility command tests.
- Updated README and V3 documentation.
- Corrected the V3-C4 commit log entry from `Pending` to `12aacfa`.

### What Problem It Solved
- Gives the project a direct command to verify the local dataset matches registry metadata.
- Makes checksum verification runnable without starting training.
- Creates the V3 reproducibility workflow entrypoint.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v3_c5_reproducibility_command.py` returned `4 passed in 0.10s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `139 passed in 1.82s`.
- `.\vir_env\Scripts\python.exe -m app.check_reproducibility` completed successfully with `status=passed`, `dataset_name=customer_churn`, `version=v1`, and matching expected/actual checksums.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status=passed`, `issues=0`, `warnings=0`, `errors=0`, and `critical=0`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after the validation gate passed.

## f5f1881 - v3-c6: close V3 reproducibility layer

### What Changed
- Marked V3 as complete in README.
- Added final V3 outcome documentation.
- Added `docs/diagrams/v3_reproducibility_flow.md`.
- Linked the V3 reproducibility diagram from the V3 overview.
- Added final V3 implementation state.
- Added final V3 closure verification notes.
- Corrected the V3-C5 commit log entry from `Pending` to `25f7c13`.

### What Problem It Solved
- Establishes a clean V3 stopping point before moving to V4.
- Makes the dataset versioning and reproducibility workflow explainable from a focused diagram.
- Preserves final verification evidence for the completed V3 layer.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `139 passed in 2.04s`.
- `.\vir_env\Scripts\python.exe -m app.check_reproducibility` completed successfully with `status=passed`, `dataset_name=customer_churn`, `version=v1`, and matching expected/actual checksums.
- `.\vir_env\Scripts\python.exe -m app.validate_data` completed successfully with `status=passed`, `issues=0`, `warnings=0`, `errors=0`, and `critical=0`.
- `.\vir_env\Scripts\python.exe -m app.train` completed successfully after the validation gate passed.
