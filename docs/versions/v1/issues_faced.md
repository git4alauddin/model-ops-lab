# V1 Issues Faced

## Issue

### Symptom
`python -m pytest -q` failed with `No module named pytest`.

### Root Cause
IDE was using a different virtual environment than the one where dependencies were installed.

### Investigation Process
- Ran `python -m pytest -q`.
- Confirmed the interpreter could not import `pytest`.

### Fix Applied
- Added `pytest` to `requirements.txt`.
- Added test files under `tests/`.
- Switched IDE interpreter to the project environment (`vir_env`).
- Re-ran tests successfully.

### Why The Fix Worked
Dependency declaration is explicit and interpreter now points to the same environment used for development.

### Prevention Strategy
Install dependencies from `requirements.txt` before running tests.

### Lessons Learned
Testing dependencies should be declared as soon as the first tests are introduced.
