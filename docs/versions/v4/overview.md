# V4 Overview

## Version Goal
Add experiment tracking, training observability, model comparison, and champion selection with MLflow.

## Completion Status
V4 is complete.

Implemented chunks:
- V4-C1: MLflow tracking foundation.
- V4-C2: failed-run tracking and evaluation duration.
- V4-C3: dedicated confusion matrix MLflow artifact.
- V4-C4: MLflow experiment comparison guide.
- V4-C5: best-run selection rule.
- V4-C6: multi-model experiment candidates and champion selection.

## Components Introduced
- MLflow dependency
- MLflow tracking configuration
- experiment tracking helper module
- MLflow run creation inside training
- multi-model experiment runner
- Logistic Regression, Decision Tree, and Random Forest candidate support
- training parameter logging
- training metric logging
- training and evaluation duration logging
- failed-run tagging for in-run failures
- training artifact logging
- dedicated confusion matrix artifact logging
- MLflow candidate tags
- MLflow champion tag
- champion selection report
- MLflow run comparison guide
- best-run selection rule
- MLflow run ID persistence in training metadata
- V4 documentation and commit log

## Workflow Introduced
Create an MLflow run for each training run.
Log model, split, dataset version, and checksum parameters.
Log evaluation metrics and runtime duration metrics.
Log local training artifacts, including the dedicated confusion matrix artifact.
Tag active runs with failure details when training fails after the run starts.
Persist the MLflow run ID in generated training metadata.
Run multiple model candidates from config.
Compare candidate runs using the documented selection rule.
Clear old champion tags and tag the current champion run.
Persist `reports/champion_run.json`.

## Engineering Objectives
- keep experiment tracking logic outside training orchestration
- make experiment tracking config-driven
- make training runs inspectable from MLflow UI
- make important evaluation outputs visible as run artifacts
- keep MLflow runtime outputs out of git
- compare real model candidates, not only repeated baseline runs
- select a champion run with reproducible criteria

## Operational Objectives
- identify each training run
- inspect parameters and metrics after training
- inspect key artifacts after training
- link experiments to dataset version metadata
- compare experiment runs from MLflow UI
- select and explain a champion run
- keep only one active champion tag after each candidate sweep

## Current V4 Outcome
V4 creates MLflow runs during training, supports multi-model candidate sweeps, logs params/metrics/artifacts, records run IDs in metadata, tracks runtime durations, tags failed in-run errors, exposes the confusion matrix as a dedicated MLflow artifact, documents run comparison, selects a champion run, tags the champion in MLflow, and writes a champion selection report.
