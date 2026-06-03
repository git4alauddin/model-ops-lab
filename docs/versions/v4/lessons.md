# V4 Lessons

- Experiment tracking should be isolated from training orchestration so it can be tested without a live tracking UI.
- MLflow 3 blocks the filesystem tracking backend by default, so local development should use SQLite unless file-store opt-out is intentional.
- Persisting the MLflow run ID in training metadata makes local artifacts traceable back to the experiment run.
