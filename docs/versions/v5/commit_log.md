# V5 Commit Log

This file records meaningful V5 commits and the operational purpose of each change.

## Pending - v5-c2: add pipeline run metadata

### What Changed
- Added `app/pipeline_run_metadata.py`.
- Added filesystem-safe pipeline run ID generation.
- Added canonical pipeline run metadata creation.
- Added stage status update helper.
- Added pass/fail completion helper.
- Added safe metadata path building.
- Added JSON persistence to `pipeline_runs/<pipeline_run_id>.json`.
- Added focused V5-C2 tests.
- Updated V5 docs and README.
- Finalized the V5-C1 commit hash as `3c8beb8`.

### What Problem It Solved
- Defines the pipeline run metadata contract before orchestration code is added.
- Separates pipeline-level run status from model metrics, training metadata, and MLflow run metadata.
- Gives future Prefect tasks one stable output shape to update.

### Verification
- `.\vir_env\Scripts\python.exe -m pytest -q tests\test_v5_c2_pipeline_run_metadata.py` returned `8 passed in 0.18s`.
- `.\vir_env\Scripts\python.exe -m pytest -q` returned `168 passed in 2.38s`.
- `git diff --check` passed with only normal Windows CRLF warnings.

## 3c8beb8 - v5-c1: add orchestration foundation

### What Changed
- Added V5 documentation scaffold.
- Added `pipeline_runs/.gitkeep` for future pipeline metadata outputs.
- Added `.gitignore` rules for future pipeline run metadata outputs.
- Added Prefect vs Airflow decision record.
- Added V5 status to README.
- Finalized the V4 diagram commit hash as `bd57557`.

### What Problem It Solved
- Establishes the orchestration boundary before runtime code is added.
- Creates the documentation structure required for V5.
- Defines where pipeline run metadata will live.
- Keeps generated pipeline run metadata out of git.
- Records the orchestration tool decision before dependency changes.

### Verification
- `Get-ChildItem docs\versions\v5` confirmed V5 docs exist.
- `Get-ChildItem pipeline_runs` confirmed `.gitkeep` exists.
- `Get-Content docs\decisions\adr_prefect_for_v5_orchestration.md` confirmed the ADR exists.
- `git diff --check` passed with only normal Windows CRLF warnings.
