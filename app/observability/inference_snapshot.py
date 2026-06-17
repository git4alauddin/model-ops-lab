"""Build production inference feature snapshots from prediction telemetry."""

from collections import Counter
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

import pandas as pd

from app.config import load_config
from app.observability.monitoring_summary import (
    DEFAULT_PREDICTION_TELEMETRY_PATH,
    load_prediction_telemetry,
)
from app.validation.checks import load_validation_schema

DEFAULT_CONFIG_PATH = Path("configs/training.yaml")
DEFAULT_INFERENCE_SNAPSHOT_PATH = Path("reports/drift/inference_snapshot.json")
FEATURE_EVENT_TYPES = {"prediction_success", "prediction_failure"}


class InferenceSnapshotError(ValueError):
    """Raised when an inference feature snapshot cannot be built."""


def build_inference_snapshot_from_config(
    config_path: Path = DEFAULT_CONFIG_PATH,
    *,
    telemetry_path: Path = DEFAULT_PREDICTION_TELEMETRY_PATH,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build an inference feature snapshot from configured schema and telemetry."""
    config = load_config(config_path)
    project_root = config_path.parent.parent
    schema_path = _resolve_project_path(
        project_root,
        config["validation"]["schema_path"],
    )
    schema = load_validation_schema(schema_path)
    telemetry_events = load_prediction_telemetry(telemetry_path)
    return build_inference_snapshot(
        telemetry_events,
        schema,
        source_path=telemetry_path,
        schema_path=schema_path,
        generated_at=generated_at,
    )


def build_inference_snapshot(
    telemetry_events: list[dict[str, Any]],
    schema: dict[str, Any],
    *,
    source_path: Path,
    schema_path: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build feature distribution summaries from feature-bearing telemetry events."""
    if not telemetry_events:
        raise InferenceSnapshotError("No prediction telemetry events provided.")

    feature_rows, skipped_events = _extract_feature_rows(telemetry_events)
    feature_columns = _feature_columns(schema)
    if feature_rows:
        dataframe = pd.DataFrame(feature_rows).reindex(columns=feature_columns)
        features = _summarize_features(dataframe, schema, feature_columns)
    else:
        features = {}

    return {
        "snapshot_version": "v1",
        "generated_at": generated_at or _utc_now(),
        "source_path": str(source_path),
        "schema_path": str(schema_path),
        "schema_name": schema.get("name"),
        "schema_version": schema.get("version"),
        "raw_event_count": len(telemetry_events),
        "feature_event_count": len(feature_rows),
        "skipped_event_count": len(skipped_events),
        "skipped_events": dict(sorted(Counter(skipped_events).items())),
        "row_count": len(feature_rows),
        "feature_count": len(features),
        "features": features,
    }


def save_inference_snapshot(
    snapshot: dict[str, Any],
    output_path: Path = DEFAULT_INFERENCE_SNAPSHOT_PATH,
) -> None:
    """Persist an inference feature snapshot as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def build_and_save_inference_snapshot(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    telemetry_path: Path = DEFAULT_PREDICTION_TELEMETRY_PATH,
    output_path: Path = DEFAULT_INFERENCE_SNAPSHOT_PATH,
) -> dict[str, Any]:
    """Build and persist the configured inference feature snapshot."""
    snapshot = build_inference_snapshot_from_config(
        config_path,
        telemetry_path=telemetry_path,
    )
    save_inference_snapshot(snapshot, output_path)
    return snapshot


def _extract_feature_rows(
    telemetry_events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    feature_rows = []
    skipped_events = []
    for event in telemetry_events:
        if event.get("event_version") != "v1":
            skipped_events.append("unsupported_or_missing_event_version")
            continue
        if event.get("event_type") not in FEATURE_EVENT_TYPES:
            skipped_events.append("unsupported_event_type")
            continue
        input_features = event.get("input_features")
        if not isinstance(input_features, dict):
            skipped_events.append("missing_input_features")
            continue
        feature_rows.append(input_features)
    return feature_rows, skipped_events


def _summarize_features(
    dataframe: pd.DataFrame,
    schema: dict[str, Any],
    feature_columns: list[str],
) -> dict[str, Any]:
    columns = schema["columns"]
    return {
        column_name: _summarize_column(
            dataframe[column_name],
            column_rules=columns[column_name],
        )
        for column_name in feature_columns
    }


def _summarize_column(
    series: pd.Series,
    *,
    column_rules: dict[str, Any],
) -> dict[str, Any]:
    dtype = str(column_rules.get("dtype"))
    common_summary = {
        "dtype": dtype,
        "role": column_rules.get("role"),
        "count": int(len(series)),
        "null_count": int(series.isna().sum()),
        "null_ratio": _rate(int(series.isna().sum()), len(series)),
    }
    if dtype in {"integer", "float"}:
        return {
            **common_summary,
            "kind": "numeric",
            "stats": _numeric_stats(series),
        }
    return {
        **common_summary,
        "kind": "categorical",
        "allowed_values": list(column_rules.get("allowed_values", [])),
        "value_counts": _value_counts(series),
        "value_ratios": _value_ratios(series),
    }


def _numeric_stats(series: pd.Series) -> dict[str, float | None]:
    numeric_series = pd.to_numeric(series, errors="coerce").dropna()
    if numeric_series.empty:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "p05": None,
            "p25": None,
            "p50": None,
            "p75": None,
            "p95": None,
        }
    return {
        "min": _round_float(numeric_series.min()),
        "max": _round_float(numeric_series.max()),
        "mean": _round_float(numeric_series.mean()),
        "std": _round_float(numeric_series.std(ddof=0)),
        "p05": _round_float(numeric_series.quantile(0.05)),
        "p25": _round_float(numeric_series.quantile(0.25)),
        "p50": _round_float(numeric_series.quantile(0.50)),
        "p75": _round_float(numeric_series.quantile(0.75)),
        "p95": _round_float(numeric_series.quantile(0.95)),
    }


def _value_counts(series: pd.Series) -> dict[str, int]:
    counts = series.astype(str).value_counts(dropna=False).sort_index()
    return {str(key): int(value) for key, value in counts.items()}


def _value_ratios(series: pd.Series) -> dict[str, float]:
    counts = _value_counts(series)
    total = sum(counts.values())
    return {key: _rate(value, total) for key, value in counts.items()}


def _feature_columns(schema: dict[str, Any]) -> list[str]:
    columns = schema.get("columns")
    if not isinstance(columns, dict):
        raise InferenceSnapshotError("Schema must define columns.")
    return [
        column_name
        for column_name, column_rules in columns.items()
        if isinstance(column_rules, dict) and column_rules.get("role") == "feature"
    ]


def _resolve_project_path(project_root: Path, configured_path: str) -> Path:
    path = Path(configured_path)
    if path.is_absolute():
        return path
    return project_root / path


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _round_float(value: Any) -> float:
    return round(float(value), 6)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
