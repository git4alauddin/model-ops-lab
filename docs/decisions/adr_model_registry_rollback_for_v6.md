# Decision: Define Local Model Registry Rollback Guardrails

## Context
V6 now supports local model registry records, candidate registration, champion promotion, single champion enforcement, and registry query inspection.

The remaining lifecycle gap is rollback.

Rollback must be defined before implementation because it changes production-style lifecycle state.

## Decision
Implement rollback later as a manual lifecycle transition:

```text
archived -> champion
current champion -> archived
```

Rollback must keep exactly one active champion for a model name.

## Rollback Rules
- Rollback target must be an existing registry record.
- Rollback target must have status `archived`.
- Current champion for the same `model_name` must be archived.
- Rollback target must become `champion`.
- Rollback must require a rollback reason.
- Rollback must preserve model lineage metadata.
- Rollback must update lifecycle metadata without changing metrics, dataset lineage, or MLflow run lineage.
- Rollback must be scoped by `model_name`.
- Rollback must not affect unrelated model names.

## Rejected Behavior
- Do not rollback directly from `candidate` to `champion`.
- Do not allow rollback without a reason.
- Do not create multiple champions for one model name.
- Do not modify experiment tracking records during rollback.
- Do not delete registry records during rollback.

## Expected Command Direction
Future implementation should add:

```text
python -m app.rollback_model
```

Expected command flow:

```text
load rollback target
verify target status is archived
find current champion for same model_name
archive current champion
promote rollback target to champion
record rollback reason
save updated registry records
```

## Consequences
- Rollback remains explicit and auditable.
- The local registry remains the source of lifecycle truth.
- MLflow remains the source of experiment tracking truth.
- Rollback can be tested with local JSON records before serving or deployment exists.

## Future Revisit Criteria
Revisit rollback behavior when:

```text
model serving is added
deployment records are added
artifact packaging is added
MLflow Model Registry integration is considered
```
