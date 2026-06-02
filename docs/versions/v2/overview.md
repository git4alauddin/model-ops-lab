# V2 Overview

## Version Goal
Add a production-style data validation and data quality layer before training.

## Components Introduced
- validation command entrypoint
- validation package
- versioned dataset schema
- validation report structure
- structural schema validation
- datatype validation
- nullability validation
- numeric range validation
- allowed-value validation
- V2 documentation and commit log

## Workflow Introduced
Validate dataset readiness before adding deeper schema and quality checks.
Compare dataset columns against the versioned schema before training.
Compare present dataframe column dtypes against schema dtype rules.
Check required fields for null values before range and category checks.
Check numeric values against schema min/max bounds.
Check controlled categorical, boolean, and target values against allowed sets.

## Engineering Objectives
- separate validation from training logic
- make dataset contracts version-controlled
- prepare for deterministic validation reports
- fail early on data problems

## Operational Objectives
- make data assumptions explicit
- create a foundation for validation logging and reports
- prepare for training pipeline integration in later chunks
