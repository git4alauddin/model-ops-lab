# V2 Issues Faced

## Open
- No open V2 implementation issues.

## Resolved

## V2-C14 Closure Evidence Gap

### Symptom
The second-pass checklist review found that corrupted dataset handling and CRITICAL severity blocking were implemented, but not explicitly covered by focused V2 tests.

### Root Cause
Those behaviors were covered indirectly through shared loader behavior and report status logic, while the checklist needed direct closure evidence.

### Investigation Process
Reviewed V2 code paths and searched the test suite for corrupted CSV handling, INFO severity behavior, CRITICAL severity behavior, and validation gate blocking coverage.

### Fix Applied
Added `tests/test_v2_c14_validation_closure.py` with explicit checks for INFO non-blocking behavior, CRITICAL blocking behavior, and safe corrupted dataset rejection.

### Why The Fix Worked
The tests now exercise the exact checklist risks instead of relying on implementation inference.

### Prevention Strategy
Before closing a version, run a checklist-to-test evidence pass and add focused closure tests for any indirectly covered behavior.

## V2-C10 Target Distribution Fixture Overlap

### Symptom
The first focused target distribution readiness tests failed with two issues instead of one.

### Root Cause
The temporary datasets only contained the `churn` column. Repeated target values made several rows exact duplicates, so the existing duplicate-row validator correctly emitted a `WARNING` alongside the new target distribution issue.

### Investigation Process
The focused test output showed both `duplicate_rows` and `target_distribution` issues in the same validation report. That meant the new validator worked, but the fixture was not isolated.

### Fix Applied
Updated the readiness fixtures to include unique `customer_id` values while keeping the same target distributions.

### Why The Fix Worked
Unique row identifiers prevented exact duplicate rows, so the readiness tests now exercise only target distribution behavior.

### Prevention Strategy
Future validation tests should include enough realistic columns to avoid accidentally triggering unrelated checks.

### Lessons Learned
As validation coverage grows, test datasets need to be intentionally shaped so each test owns one failure mode.
