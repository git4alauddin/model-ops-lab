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
- dataset checksum metadata
- dataset checksum calculation and validation helpers
- reproducibility check command
- V3 documentation and commit log

## Workflow Introduced
Record the current dataset as an explicit versioned registry entry.
Load dataset version metadata through a controlled application module.
Keep dataset path, schema path, target column, and ownership metadata in one inspectable place.
Record dataset version metadata in training artifacts.
Record dataset version metadata in validation reports.
Record the dataset file SHA256 checksum in the dataset registry.
Check that the current local dataset still matches the registered checksum.

## Engineering Objectives
- make dataset versions explicit
- keep dataset metadata version-controlled
- create a reusable loading path before adding checksum and reproducibility checks
- connect dataset version metadata to model training outputs
- connect dataset version metadata to validation outputs
- track dataset file content identity with checksums
- expose reproducibility checks through a command

## Operational Objectives
- answer which dataset version is being used
- make dataset metadata easy to inspect
- make training artifacts trace back to a dataset version
- make validation reports trace back to a dataset version
- make dataset content changes detectable
- provide a quick local reproducibility check before training or review

## Current V3 Outcome
V3-C5 adds a command that verifies the local dataset matches the registered dataset version checksum.
