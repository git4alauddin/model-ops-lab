# V6 Commit Log

This file records meaningful V6 commits and the operational purpose of each change.

## Pending - v6-c1: add model registry foundation

### What Changed
- Added V6 documentation scaffold.
- Added model registry overview.
- Added model registry implementation plan.
- Added V6 verification, issues, lessons, and commit log files.
- Added ADR for starting with a local model registry.
- Added V6 status to README.
- Finalized the V5-C12 commit hash as `e8cd385`.

### What Problem It Solved
- Defines the model registry boundary before runtime code is added.
- Separates experiment tracking from model version lifecycle management.
- Records the initial decision to start with local project registry metadata.

### Verification
- Verified V6 documentation scaffold exists.
- Verified README includes V6 status.
- Verified V5-C12 commit hash is finalized as `e8cd385`.
- Ran `git diff --check`; it passed with normal LF-to-CRLF working-copy warnings only.
