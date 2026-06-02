# V1 Lessons

- Scaffolding before logic reduces accidental coupling.
- External config path early prevents hardcoded training setup.
- Documentation-first structure makes later traceability easier.
- Validating config before data access surfaces errors earlier and clearer.
- Controlled dataset load failures improve debugging and operational safety.
- Test dependencies must be declared and installed before test execution checkpoints.
- Feature-target splitting should be centralized to prevent target leakage.
- A dataset with only the target column is invalid for training even if it loads successfully.
- Train-test splitting must use config values so model results are reproducible.
- Reproducibility checks should test stable row partitions, not only row counts.
