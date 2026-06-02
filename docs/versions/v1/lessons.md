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
- Feature type detection should fail loudly on unsupported dtypes to avoid silent column loss.
- `OneHotEncoder(handle_unknown="ignore")` prevents unseen categories from breaking future inference.
- Preprocessing construction should be reusable and separate from training orchestration.
- Combining preprocessing and model in one sklearn pipeline prevents training-serving skew later.
- Model construction should reject unsupported config values before training begins.
- Training duration should be tracked from the first baseline so later automation has timing context.
- A small local smoke dataset is useful for proving success paths before artifact persistence exists.
- Identifier columns should be dropped explicitly through config instead of being silently used as model features.
