# V6 Implementation

## Scope
V6 adds model registry and promotion lifecycle foundations.

V6 started documentation-first: define the registry approach, lifecycle vocabulary, and boundaries before adding runtime code.

Implemented chunks:
- V6-C1: model registry foundation and decision record.
- V6-C2: model registry metadata contract.
- V6-C3: model registry metadata persistence.
- V6-C4: model registration command.
- V6-C5: champion promotion command.
- V6-C6: single champion enforcement.

## V6-C1 Additions
- `docs/versions/v6/`
  - added V6 overview, implementation, verification, issues, lessons, and commit log files
- `docs/decisions/adr_local_model_registry_for_v6.md`
  - records the decision to start with a local project registry before direct MLflow Model Registry integration
- `README.md`
  - adds V6 status and direction
- `docs/versions/v5/commit_log.md`
  - finalizes the V5-C12 commit hash

## V6-C2 Additions
- `app/model_registry.py`
  - defines lifecycle states: `candidate`, `champion`, `archived`
  - defines the model version metadata builder
  - validates required model registry fields
  - validates lifecycle state values
  - validates metrics are present and numeric
  - validates optional promotion fields when provided
- `model_registry/.gitkeep`
  - creates the local registry folder placeholder
- `tests/test_v6_c2_model_registry_contract.py`
  - verifies the canonical metadata shape
  - verifies missing required fields are rejected
  - verifies invalid lifecycle states are rejected
  - verifies all supported lifecycle states are accepted
  - verifies metric values must be numeric

## V6-C3 Additions
- `app/model_registry.py`
  - builds filesystem-safe registry metadata paths
  - saves validated model version metadata as JSON
  - loads saved model version metadata from JSON
  - validates loaded metadata before returning it
  - rejects unsafe model names and model versions
- `.gitignore`
  - ignores generated `model_registry/` runtime JSON files
  - keeps `model_registry/.gitkeep` tracked
- `tests/test_v6_c3_model_registry_persistence.py`
  - verifies safe registry filename construction
  - verifies valid metadata can be saved
  - verifies saved metadata can be loaded
  - verifies unsafe model names are rejected
  - verifies unsafe model versions are rejected
  - verifies invalid loaded metadata is rejected

## V6-C4 Additions
- `app/register_model.py`
  - reads `reports/champion_run.json`
  - extracts the selected champion run
  - builds model registry metadata from champion lineage and metrics
  - registers the model as `candidate`
  - persists the registry record under `model_registry/`
  - fails clearly when the champion report is missing or incomplete
- `tests/test_v6_c4_register_model_command.py`
  - verifies successful registration from a champion report
  - verifies explicit model version override
  - verifies missing champion report failure
  - verifies missing champion object failure
  - verifies incomplete champion fields fail clearly

## V6-C5 Additions
- `app/model_registry.py`
  - adds lifecycle status update helper
  - preserves previous status in `promoted_from`
  - updates `updated_at` during lifecycle changes
  - validates metadata after lifecycle updates
- `app/promote_model.py`
  - loads a registered model version from `model_registry/`
  - requires the current status to be `candidate`
  - updates the selected version to `champion`
  - persists the promotion reason
  - saves the promoted registry record
  - fails clearly when the record is missing or not a candidate
- `tests/test_v6_c5_promote_model_command.py`
  - verifies candidate promotion to champion
  - verifies promotion reason persistence
  - verifies missing model record failure
  - verifies non-candidate promotion is rejected
  - verifies default model version resolution from champion report

## V6-C6 Additions
- `app/model_registry.py`
  - lists local model registry records
  - finds champion records for a model name
  - archives existing champions for the same model name
  - validates registry records while listing them
- `app/promote_model.py`
  - archives existing champions before promoting the selected candidate
  - keeps unrelated model champions unchanged
  - keeps candidate-only promotion guard
- `tests/test_v6_c6_single_champion.py`
  - verifies promoting a candidate archives an existing champion
  - verifies the promoted candidate is the only champion for its model name
  - verifies unrelated model champions are not archived
  - verifies non-candidate promotion still fails without archiving

## Registry Boundary
V6 should not replace MLflow experiment tracking.

Current responsibilities:

```text
MLflow = experiment runs, params, metrics, artifacts
V6 registry = project-level model versions and promotion state
```

## Planned V6 Runtime Direction
Future V6 chunks should introduce:

```text
tests/test_v6_*.py
```

Expected registry record fields:

```text
model_name
model_version
status
registry_version
created_at
updated_at
mlflow_run_id
candidate_name
model_type
dataset_name
dataset_version
dataset_checksum
metrics
artifact_uri
promoted_from
promotion_reason
```

## Design Guardrail
Start with explicit manual promotion.

Do not automatically promote every champion report into a registry champion until the registry contract and rollback behavior are tested.

## Remaining V6 Gaps
- Registry diagram is not added yet.
- Rollback behavior is not added yet.
