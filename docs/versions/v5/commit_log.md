# V5 Commit Log

This file records meaningful V5 commits and the operational purpose of each change.

## Pending - v5-c1: add orchestration foundation

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
