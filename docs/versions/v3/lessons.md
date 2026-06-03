# V3 Lessons

- Dataset versioning should start with simple metadata before adding enforcement.
- A small registry loader keeps future training and validation integrations from reading YAML ad hoc.
- Version metadata should point to both the physical dataset and the schema that validates it.
- Training metadata is the first practical place to connect models back to dataset versions.
- Validation reports should carry dataset version metadata because they prove whether a specific dataset version passed quality gates.
- Dataset version names need checksums because a filename can stay the same while file content changes.
