## ModelOpsLab

Production-style, versioned MLOps project built incrementally.

### V1 Status

V1 chunks 1-10 completed:
- app entrypoints and modules
- config template
- config validation + robust dataset loading
- feature-target split
- train-test split
- feature type detection
- preprocessing pipeline construction
- baseline model training
- sample churn dataset smoke run
- evaluation metrics
- artifact persistence
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
    test_v1_c2_config_validation.py
    test_v1_c2_dataset_loading.py
    test_v1_c3_feature_target_split.py
    test_v1_c4_train_test_split.py
    test_v1_c5_feature_type_detection.py
    test_v1_c6_preprocessing_pipeline.py
    test_v1_c7_baseline_model_training.py
    test_v1_c8_sample_churn_dataset.py
    test_v1_c9_evaluation_metrics.py
    test_v1_c10_artifact_persistence.py
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
