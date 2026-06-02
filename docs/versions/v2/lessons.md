# V2 Lessons

- Validation should be a separate layer from training orchestration.
- Schema rules should be versioned because dataset contracts change over time.
- A validation report object gives later checks one consistent output shape.
- Starting with schema loading keeps V2 grounded before adding many checks.
- Structural validation should happen before dtype, null, range, and category checks.
- Missing and unexpected columns are blocking schema drift signals.
