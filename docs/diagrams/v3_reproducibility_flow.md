# V3 Reproducibility Flow

This diagram shows the completed V3 dataset versioning and reproducibility workflow.

It is intentionally limited to V3 scope: dataset registry metadata, checksum tracking, reproducibility checks, and dataset version traceability in validation and training outputs.

```mermaid
flowchart TD
    config["configs/training.yaml"]
    metadata["data_versions/customer_churn/v1.yaml"]
    dataset["data/churn.csv"]
    schema["schema_versions/customer_churn_v1.yaml"]

    registry["Dataset registry loader"]
    checksum["SHA256 checksum validation"]
    repro["python -m app.check_reproducibility"]

    validation["python -m app.validate_data"]
    training["python -m app.train"]

    validation_report["reports/validation_report.json"]
    validation_summary["reports/validation_summary.txt"]
    training_metadata["artifacts/training_metadata.json"]
    logs["logs/modelopslab.log"]

    pass["Reproducibility passed"]
    fail["Fail safely on mismatch"]

    config --> registry
    metadata --> registry
    dataset --> checksum
    metadata --> checksum
    schema --> validation

    registry --> repro
    checksum --> repro
    repro --> pass
    repro --> fail
    repro --> logs

    registry --> validation
    checksum --> validation_report
    validation --> validation_report
    validation --> validation_summary
    validation --> logs

    registry --> training
    checksum --> training_metadata
    training --> training_metadata
    training --> logs
```

## Operational Meaning

V3 makes dataset identity explicit and verifiable.

The dataset registry records which dataset version is active and which checksum the physical dataset file must match. The reproducibility command verifies that local file content still matches the registered version, while validation reports and training metadata preserve the dataset version and checksum used by each run.
