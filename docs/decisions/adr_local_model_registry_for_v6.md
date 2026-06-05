# Decision: Start V6 With A Local Model Registry

## Context
V6 introduces model registry and promotion lifecycle foundations.

The project already has:

```text
MLflow experiment tracking
multi-model candidate runs
champion selection report
champion tagging in MLflow
pipeline-level orchestration metadata
```

The missing layer is a project-level model version lifecycle.

## Decision
Start V6 with a local project model registry.

Do not depend on MLflow Model Registry as the first registry implementation.

Keep MLflow as the experiment tracking system.

## Why Local Registry First
- Easier to inspect during learning.
- Easier to test without relying on MLflow registry behavior.
- Keeps model version metadata under a project-owned contract.
- Avoids mixing experiment tracking decisions with promotion lifecycle decisions too early.
- Lets the project define promotion states before integrating deeper tooling.

## Why Not MLflow Model Registry First
- It introduces additional MLflow concepts before the project owns its registry contract.
- Local SQLite-backed MLflow registry behavior can be environment-sensitive.
- The project still needs explicit promotion semantics even if MLflow registry is used later.
- Starting local keeps V6 focused on lifecycle design, not tool-specific registry operations.

## Initial Lifecycle States

```text
candidate
champion
archived
```

## Expected Local Registry Direction
Future chunks should add project-owned registry records, likely under:

```text
model_registry/
```

Each registered model version should reference:

```text
MLflow run ID
candidate name
model type
dataset version
dataset checksum
metrics
artifact location
promotion status
```

## Consequences
- MLflow remains the source for experiment run details.
- The local registry becomes the source for model version lifecycle state.
- Promotion can be implemented as a deliberate command.
- Registry records can be tested with normal file-based tests.

## Revisit Criteria
Revisit MLflow Model Registry integration when:

```text
local registry contract is stable
promotion and archive behavior is tested
serving or deployment needs registered model URIs
model stage transitions need to be visible inside MLflow UI
```
