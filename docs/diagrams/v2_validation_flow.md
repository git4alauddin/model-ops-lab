# V2 Validation Flow

This diagram shows the completed V2 data validation flow.

It is intentionally limited to V2 scope: schema checks, data quality checks, report persistence, readable logs, and the training validation gate.

```mermaid
flowchart TD
    config["configs/training.yaml"]
    dataset["data/churn.csv"]
    schema["schema_versions/customer_churn_v1.yaml"]

    command["python -m app.validate_data"]

    checks["Validation checks"]
    structural["Schema structure"]
    dtype["Datatypes"]
    nullability["Nullability"]
    null_pct["Null percentages"]
    ranges["Numeric ranges"]
    outliers["Outlier sanity"]
    allowed["Allowed values"]
    duplicates["Duplicates"]
    target["Target distribution"]

    report["reports/validation_report.json"]
    summary["reports/validation_summary.txt"]
    logs["logs/modelopslab.log"]

    gate["Training validation gate"]
    train["python -m app.train"]
    stop["Stop training on failed validation"]
    continue["Continue when validation passed"]

    config --> command
    dataset --> command
    schema --> command

    command --> checks

    checks --> structural
    checks --> dtype
    checks --> nullability
    checks --> null_pct
    checks --> ranges
    checks --> outliers
    checks --> allowed
    checks --> duplicates
    checks --> target

    structural --> report
    dtype --> report
    nullability --> report
    null_pct --> report
    ranges --> report
    outliers --> report
    allowed --> report
    duplicates --> report
    target --> report

    report --> summary
    report --> logs

    report --> gate
    train --> gate
    gate --> stop
    gate --> continue
```

## Operational Meaning

V2 makes data validation a first-class step before training.

The validation command loads the configured dataset and versioned schema, runs deterministic checks, persists machine-readable and human-readable reports, writes readable logs, and supplies the training gate with a pass/fail decision.
