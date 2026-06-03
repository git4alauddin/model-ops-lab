# V3 Overview

## Version Goal
Make datasets versioned, traceable, and reproducible.

## Completion Status
V3 is in progress.

## Components Introduced
- dataset version registry folder
- first customer churn dataset version metadata file
- dataset registry metadata loader
- dataset registry metadata validation
- training metadata dataset version persistence
- validation report dataset version persistence
- V3 documentation and commit log

## Workflow Introduced
Record the current dataset as an explicit versioned registry entry.
Load dataset version metadata through a controlled application module.
Keep dataset path, schema path, target column, and ownership metadata in one inspectable place.
Record dataset version metadata in training artifacts.
Record dataset version metadata in validation reports.

## Engineering Objectives
- make dataset versions explicit
- keep dataset metadata version-controlled
- create a reusable loading path before adding checksum and reproducibility checks
- connect dataset version metadata to model training outputs
- connect dataset version metadata to validation outputs

## Operational Objectives
- answer which dataset version is being used
- make dataset metadata easy to inspect
- make training artifacts trace back to a dataset version
- make validation reports trace back to a dataset version

## Current V3 Outcome
V3-C3 records the active dataset version in generated validation reports.
