# Decision: Use Prefect For V5 Orchestration

## Context
V5 introduces training pipeline automation and workflow orchestration.

The project already has stable local commands:

```powershell
python -m app.train
python -m app.run_experiments
```

The next layer should coordinate proven behavior instead of replacing it too early.

## Decision
Use Prefect as the first orchestration tool for V5.

Do not add Airflow in the initial orchestration chunk.

Do not replace the existing training and experiment commands during the foundation step.

## Why Prefect
- Lower local setup overhead than Airflow.
- Clear flow and task concepts for learning orchestration.
- Good fit for local development before scheduling infrastructure exists.
- Supports retries, task state, and pipeline observability when the project is ready for them.
- Lets the project introduce orchestration incrementally around existing Python code.

## Why Not Airflow Yet
- Airflow is heavier to run locally.
- It introduces scheduler, metadata database, DAG parsing, and service-management concerns earlier than needed.
- It is useful later, but too much operational surface area for the first orchestration layer.

## Consequences
- Future V5 chunks should add a Prefect dependency and a pipeline entrypoint.
- Existing commands remain valid while orchestration is introduced.
- Pipeline metadata should be persisted under `pipeline_runs/`.
- The pipeline should expose stage-level status, failed stage, dataset version, config path, MLflow run IDs, and champion run ID.

## Revisit Criteria
Revisit Airflow later if the project needs production-style scheduling, backfills, external task dependencies, or stronger DAG operations.
