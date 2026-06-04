# V5 Lessons

- Orchestration should be introduced around stable behavior, not by replacing working commands immediately.
- A pipeline run needs its own metadata because workflow status is different from model metrics or MLflow run metadata.
- Prefect is a better initial fit than Airflow for this project because it gives orchestration concepts with lower local setup overhead.
- A metadata contract should exist before orchestration code so future tasks write consistent run records.
- Pipeline metadata should be immutable-by-default during updates where practical; returning updated copies avoids accidental stage-state mutation.
