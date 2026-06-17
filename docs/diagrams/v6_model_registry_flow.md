# V6 Model Registry Flow

This diagram shows the current V6 model registry lifecycle.

It is intentionally limited to implemented V6 behavior: local registry metadata, champion registration, candidate promotion, single champion enforcement, archive handling, and registry query inspection.

```mermaid
flowchart TD
    subgraph champion_input["Champion selection input"]
        champion_report["reports/champion_run.json<br/>selected experiment winner"]
    end

    subgraph registry_contract_layer["Registry contract"]
        registry_contract["app.model_registry<br/>metadata contract + validation"]
    end

    subgraph registration_flow["Registration flow"]
        register_cmd["python -m app.register_model"]
        candidate_record["model_registry/<model>__<version>.json<br/>status=candidate"]
    end

    subgraph promotion_flow["Promotion flow"]
        promote_cmd["python -m app.promote_model"]
        existing_champion{"Existing champion<br/>for same model_name?"}
        archived_record["previous champion record<br/>status=archived"]
        champion_record["selected model record<br/>status=champion"]
    end

    subgraph inspection_flow["Inspection flow"]
        query_cmd["python -m app.query_model_registry"]
        summary["Registry summary<br/>current champion + versions"]
    end

    subgraph registry_storage["Local registry storage"]
        ignored_runtime["model_registry/*.json<br/>ignored runtime metadata"]
        tracked_placeholder["model_registry/.gitkeep<br/>tracked folder placeholder"]
    end

    champion_report --> register_cmd
    register_cmd --> registry_contract
    registry_contract --> candidate_record
    candidate_record --> ignored_runtime
    tracked_placeholder -. keeps folder .-> ignored_runtime

    candidate_record --> promote_cmd
    promote_cmd --> existing_champion
    existing_champion -- yes --> archived_record
    existing_champion -- no --> champion_record
    archived_record --> champion_record
    champion_record --> ignored_runtime

    ignored_runtime --> query_cmd
    query_cmd --> registry_contract
    registry_contract --> summary
```

## Operational Meaning

V6 turns the V4 champion decision into a managed model lifecycle record.

The registration command reads the champion report and writes a candidate model version into the local registry. Promotion is a separate command. It only promotes candidate records, archives any previous champion for the same model name, and keeps unrelated model champions untouched. Querying the registry gives a command-level view of the current champion and registered versions without opening JSON files manually.

The local registry is project metadata, not MLflow tracking storage. MLflow still owns experiment runs, metrics, params, and run artifacts. The V6 registry owns model version lifecycle state.

## Current Boundary

The registry is local and file-based.

Generated registry JSON files are ignored by git. The repository tracks only the `model_registry/.gitkeep` placeholder and the code/docs that define the registry behavior.

Rollback behavior is not implemented yet.
