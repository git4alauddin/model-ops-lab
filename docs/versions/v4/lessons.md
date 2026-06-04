# V4 Lessons

- Experiment tracking should be isolated from training orchestration so it can be tested without a live tracking UI.
- MLflow 3 blocks the filesystem tracking backend by default, so local development should use SQLite unless file-store opt-out is intentional.
- Persisting the MLflow run ID in training metadata makes local artifacts traceable back to the experiment run.
- Runtime duration values are useful MLflow metrics because they support comparison beyond model quality.
- Failed-run details should be logged as tags because failure metadata describes the run, not model performance.
- A context manager that wraps training must preserve the original body exception; otherwise debugging points at the tracking layer instead of the real failure.
- Fake MLflow tests validate tracking calls quickly, but real `python -m app.train` verification is still needed to cover dependency loading and backend behavior.
- Important evaluation outputs should be logged as dedicated artifacts when they are useful to inspect directly in the MLflow UI.
- Run comparison should check params, metrics, artifacts, and dataset checksum together; metrics alone can hide setup differences.
