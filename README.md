## ModelOpsLab

Production-style, versioned MLOps project built incrementally.

### V1 Status

V1 chunks 1-2 completed:
- app entrypoints and modules
- config template
- config validation + robust dataset loading
- focused tests for config and dataset loader
- docs structure
- environment and dependency files

### Expected Structure

```text
modelOpsLab/
  app/
    train.py
    evaluate.py
    config.py
    schemas.py
    pipeline/
    utils/
  configs/
    training.yaml
  tests/
    test_v1_config_validation.py
    test_v1_dataset_loading.py
  data/
  artifacts/
  docs/
    versions/v1/
    architecture/
    decisions/
    experiments/
    incidents/
    deployment/
    observability/
    diagrams/
```

### Next Step

Implement V1 dataset loading, preprocessing, and training flow in small chunks.
