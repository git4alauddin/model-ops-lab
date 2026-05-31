## ModelOpsLab

Production-style, versioned MLOps project built incrementally.

### V1 Status

V1 chunk 1 scaffolding is in place:
- app entrypoints and modules
- config template
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
