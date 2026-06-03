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
- V3 documentation and commit log

## Workflow Introduced
Record the current dataset as an explicit versioned registry entry.
Load dataset version metadata through a controlled application module.
Keep dataset path, schema path, target column, and ownership metadata in one inspectable place.

## Engineering Objectives
- make dataset versions explicit
- keep dataset metadata version-controlled
- create a reusable loading path before adding checksum and reproducibility checks

## Operational Objectives
- answer which dataset version is being used
- make dataset metadata easy to inspect
- prepare training and validation to record dataset version information later

## Current V3 Outcome
V3-C1 establishes the dataset registry foundation for the current churn dataset.
