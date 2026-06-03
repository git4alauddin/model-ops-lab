# V2 Issues Faced

## Open
- No V2 implementation issues recorded yet.

## Resolved

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
