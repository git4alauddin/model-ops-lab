# V4 Overview

## Version Goal
Add experiment tracking and training observability with MLflow.

## Completion Status
V4 is complete.

Implemented chunks:
- V4-C1: MLflow tracking foundation.
- V4-C2: failed-run tracking and evaluation duration.
- V4-C3: dedicated confusion matrix MLflow artifact.
- V4-C4: MLflow experiment comparison guide.
- V4-C5: best-run selection rule.

## Components Introduced
- MLflow dependency
- MLflow tracking configuration
- experiment tracking helper module
- MLflow run creation inside training
- training parameter logging
- training metric logging
- training and evaluation duration logging
- failed-run tagging for in-run failures
- training artifact logging
- dedicated confusion matrix artifact logging
- manual MLflow run comparison guide
- manual best-run selection rule
- MLflow run ID persistence in training metadata
- V4 documentation and commit log

## Workflow Introduced
Create an MLflow run for each training run.
Log model, split, dataset version, and checksum parameters.
Log evaluation metrics and runtime duration metrics.
Log local training artifacts, including the dedicated confusion matrix artifact.
Tag active runs with failure details when training fails after the run starts.
Persist the MLflow run ID in generated training metadata.
Compare runs from MLflow UI using params, metrics, artifacts, and dataset checksum.
Select the best eligible run using a documented F1-first rule.

## Engineering Objectives
- keep experiment tracking logic outside training orchestration
- make experiment tracking config-driven
- make training runs inspectable from MLflow UI
- make important evaluation outputs visible as run artifacts
- keep MLflow runtime outputs out of git
- document run comparison and selection before automating best-run logic

## Operational Objectives
- identify each training run
- inspect parameters and metrics after training
- inspect key artifacts after training
- link experiments to dataset version metadata
- compare experiment runs from MLflow UI
- select a best run with a consistent manual rule

## Current V4 Outcome
V4 creates MLflow runs during training, logs params/metrics/artifacts, records run IDs in metadata, tracks runtime durations, tags failed in-run errors, exposes the confusion matrix as a dedicated MLflow artifact, documents how to compare runs manually, and defines a best-run selection rule.
