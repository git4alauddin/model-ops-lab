# V6 Lessons

- Champion selection is not the same as model registry management.
- MLflow run IDs should be preserved as lineage references inside registry records.
- A local registry contract is easier to test and inspect before using external registry features.
- Promotion should start as an explicit manual action before becoming automated.
- A model registry needs a validated metadata contract before it needs persistence or UI features.
- Lifecycle state names should be project-owned first, then mapped to external registry tooling later if needed.
- Registry persistence should validate both before saving and after loading.
- Registry filenames must be safe because model names and versions become filesystem paths.
- Champion selection is an experiment decision; registration turns that decision into a managed model lifecycle record.
- Registration should create a `candidate` first, not a `champion`, so promotion stays explicit.
- Promotion should reject non-candidate records to prevent accidental lifecycle rewrites.
- Promotion should persist both the reason and the previous lifecycle state for auditability.
- A registry should make the active champion unambiguous for each model name.
- Promotion should scope champion replacement by model name so unrelated models are not affected.
- Registry metadata should be queryable without manually opening JSON files.
- Query commands should summarize the operational state instead of dumping raw metadata.
