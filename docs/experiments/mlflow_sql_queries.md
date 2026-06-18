# Helpful MLflow SQLite Queries

Use these in the PyCharm DB console connected to `modelOpsLab/mlflow.db`.

```sql
-- 1. List MLflow experiments
SELECT *
FROM experiments;
```

```sql
-- 2. List runs
SELECT
  run_uuid,
  name,
  status,
  experiment_id,
  datetime(start_time / 1000, 'unixepoch') AS started_at,
  datetime(end_time / 1000, 'unixepoch') AS ended_at
FROM runs
ORDER BY start_time DESC;
```

```sql
-- 3. Runs with experiment name
SELECT
  e.name AS experiment_name,
  r.run_uuid,
  r.name AS run_name,
  r.status,
  datetime(r.start_time / 1000, 'unixepoch') AS started_at
FROM runs r
JOIN experiments e ON r.experiment_id = e.experiment_id
ORDER BY r.start_time DESC;
```

```sql
-- 4. Params for latest run
SELECT
  p.key,
  p.value
FROM params p
WHERE p.run_uuid = (
  SELECT run_uuid
  FROM runs
  ORDER BY start_time DESC
  LIMIT 1
)
ORDER BY p.key;
```

```sql
-- 5. Metrics for latest run
SELECT
  m.key,
  m.value
FROM latest_metrics m
WHERE m.run_uuid = (
  SELECT run_uuid
  FROM runs
  ORDER BY start_time DESC
  LIMIT 1
)
ORDER BY m.key;
```

```sql
-- 6. Run summary with selected params and metrics
SELECT
  r.run_uuid,
  r.status,
  MAX(CASE WHEN p.key = 'model_type' THEN p.value END) AS model_type,
  MAX(CASE WHEN p.key = 'dataset_version' THEN p.value END) AS dataset_version,
  MAX(CASE WHEN m.key = 'accuracy' THEN m.value END) AS accuracy,
  MAX(CASE WHEN m.key = 'f1' THEN m.value END) AS f1
FROM runs r
LEFT JOIN params p ON r.run_uuid = p.run_uuid
LEFT JOIN latest_metrics m ON r.run_uuid = m.run_uuid
GROUP BY r.run_uuid, r.status
ORDER BY r.start_time DESC;
```

```sql
-- 7. Find best runs by accuracy
SELECT
  r.run_uuid,
  r.status,
  m.value AS accuracy
FROM runs r
JOIN latest_metrics m ON r.run_uuid = m.run_uuid
WHERE m.key = 'accuracy'
ORDER BY m.value DESC
LIMIT 5;
```

```sql
-- 8. Dataset/version traceability
SELECT
  r.run_uuid,
  MAX(CASE WHEN p.key = 'dataset_name' THEN p.value END) AS dataset_name,
  MAX(CASE WHEN p.key = 'dataset_version' THEN p.value END) AS dataset_version,
  MAX(CASE WHEN p.key = 'dataset_checksum' THEN p.value END) AS dataset_checksum
FROM runs r
LEFT JOIN params p ON r.run_uuid = p.run_uuid
GROUP BY r.run_uuid
ORDER BY r.start_time DESC;
```

```sql
-- 9. Artifact locations
SELECT
  run_uuid,
  artifact_uri
FROM runs
ORDER BY start_time DESC;
```

```sql
-- 10. Count runs per experiment
SELECT
  e.name AS experiment_name,
  COUNT(r.run_uuid) AS run_count
FROM experiments e
LEFT JOIN runs r ON e.experiment_id = r.experiment_id
GROUP BY e.name;
```

## Good first queries

```sql
SELECT * FROM experiments;
SELECT * FROM runs;
SELECT * FROM params;
SELECT * FROM latest_metrics;
```
