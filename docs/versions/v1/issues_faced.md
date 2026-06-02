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

## Issue

### Symptom
`test_evaluate_model_confusion_matrix_shape` failed because the confusion matrix was `1x1` instead of `2x2`.

### Root Cause
The small evaluation split contained only one class in `y_true` and `y_pred`. By default, sklearn infers labels from observed values, so it returned a confusion matrix for only the observed class.

### Investigation Process
- Ran `python -m pytest -q`.
- Observed one failure in `tests/test_v1_c9_evaluation_metrics.py`.
- Confirmed sklearn warning recommended passing explicit labels.

### Fix Applied
- Updated `confusion_matrix` call to use `labels=[0, 1]`.

### Why The Fix Worked
The evaluation output now always uses the binary churn class space, even when a tiny test split observes only one class.

### Prevention Strategy
For binary classification metrics that must have stable shape, pass explicit labels instead of relying on inferred labels.

### Lessons Learned
Small smoke datasets can expose metric-shape edge cases that larger datasets may hide.
