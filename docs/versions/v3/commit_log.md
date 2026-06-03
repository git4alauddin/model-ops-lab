# V3 Commit Log

This file records meaningful V3 commits and the operational purpose of each change.

## Pending - v3-c1: add dataset registry foundation

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
