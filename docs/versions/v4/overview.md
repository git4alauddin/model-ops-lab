# V4 Overview

## Version Goal
Add experiment tracking and training observability with MLflow.

## Completion Status
V4 is in progress.

## Components Introduced
- MLflow dependency
- MLflow tracking configuration
- experiment tracking helper module
- MLflow run creation inside training
- training parameter logging
- training metric logging
- training artifact logging
- MLflow run ID persistence in training metadata
- V4 documentation and commit log

## Workflow Introduced
Create an MLflow run for each training run.
Log model, split, dataset version, and checksum parameters.
Log evaluation metrics.
Log local training artifacts.
Persist the MLflow run ID in generated training metadata.

## Engineering Objectives
- keep experiment tracking logic outside training orchestration
- make experiment tracking config-driven
- make training runs inspectable from MLflow UI
- keep MLflow runtime outputs out of git

## Operational Objectives
- identify each training run
- inspect parameters and metrics after training
- link experiments to dataset version metadata
- compare future experiment runs from MLflow UI

## Current V4 Outcome
V4-C1 creates MLflow runs during training and records the run ID in training metadata.
