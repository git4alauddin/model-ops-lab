# V2 Overview

## Version Goal
Add a production-style data validation and data quality layer before training.

## Completion Status
V2 is complete.

## Components Introduced
- validation command entrypoint
- validation package
- versioned dataset schema
- validation report structure
- structural schema validation
- datatype validation
- nullability validation
- null percentage validation
- numeric range validation
- outlier sanity validation
- allowed-value validation
- duplicate validation
- target distribution sanity checks
- validation report persistence
- validation metadata persistence
- training validation gate
- formatted validation runtime logs
- V2 documentation and commit log

## Workflow Introduced
Validate dataset readiness before adding deeper schema and quality checks.
Compare dataset columns against the versioned schema before training.
Compare present dataframe column dtypes against schema dtype rules.
Check required fields for null values before range and category checks.
Check nullable fields for excessive missingness.
Check numeric values against schema min/max bounds.
Check suspicious numeric feature outliers.
Check controlled categorical, boolean, and target values against allowed sets.
Check duplicate rows and duplicate entity IDs.
Check target class distribution before training.
Persist validation reports for auditability and local inspection.
Persist validation runtime metadata for traceability.
Block training when validation reports blocking data quality failures.
Expose readable validation logs for local debugging.

## Engineering Objectives
- separate validation from training logic
- make dataset contracts version-controlled
- persist deterministic validation reports
- fail early on data problems
- keep validation behavior reusable from training

## Operational Objectives
- make data assumptions explicit
- create readable validation logs and reports
- integrate validation into the training workflow
- make validation outcomes reproducible and inspectable

## Final V2 Outcome
V2 turns the project from a training-only workflow into a validation-first workflow.

The validation layer now catches schema drift, datatype mismatches, required-field nulls, excessive missingness, hard numeric range violations, suspicious numeric outliers, invalid controlled values, duplicate records, duplicate IDs, and unusable target distributions before training.

## Diagram
- `docs/diagrams/v2_validation_flow.md`
