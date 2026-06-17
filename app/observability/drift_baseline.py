"""Build reference baselines for future drift detection."""

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

import pandas as pd

from app.config import load_config
from app.data import load_dataset
from app.validation.checks import load_validation_schema

DEFAULT_CONFIG_PATH = Path("configs/training.yaml")
DEFAULT_DRIFT_BASELINE_PATH = Path("reports/drift/reference_baseline.json")
NUMERIC_DTYPES = {"integer", "float"}
CATEGORICAL_DTYPES = {"boolean", "category", "string"}


class DriftBaselineError(ValueError):
    """Raised when a drift reference baseline cannot be built."""


def build_reference_baseline_from_config(
    config_path: Path = DEFAULT_CONFIG_PATH,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a drift reference baseline from the configured training dataset."""
    config = load_config(config_path)
    project_root = config_path.parent.parent
    dataset_path = _resolve_project_path(project_root, config["dataset"]["path"])
    schema_path = _resolve_project_path(
        project_root,
        config["validation"]["schema_path"],
    )
    dataframe = load_dataset(dataset_path)
    schema = load_validation_schema(schema_path)

    return build_reference_baseline(
        dataframe,
        schema,
        dataset_path=dataset_path,
        schema_path=schema_path,
        generated_at=generated_at,
    )


def build_reference_baseline(
    dataframe: pd.DataFrame,
    schema: dict[str, Any],
    *,
    dataset_path: Path,
    schema_path: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build feature and target distribution summaries for drift detection."""
    if dataframe.empty:
        raise DriftBaselineError("Cannot build drift baseline from an empty dataset.")

    columns = schema.get("columns")
    if not isinstance(columns, dict):
        raise DriftBaselineError("Schema must define columns.")

    feature_columns = _columns_by_role(columns, "feature")
    target_columns = _columns_by_role(columns, "target")
    features = {
        column_name: _summarize_column(
            dataframe,
            column_name=column_name,
            column_rules=columns[column_name],
        )
        for column_name in feature_columns
    }
    targets = {
        column_name: _summarize_column(
            dataframe,
            column_name=column_name,
            column_rules=columns[column_name],
        )
        for column_name in target_columns
    }

    return {
        "baseline_version": "v1",
        "generated_at": generated_at or _utc_now(),
        "dataset_path": str(dataset_path),
        "schema_path": str(schema_path),
        "schema_name": schema.get("name"),
        "schema_version": schema.get("version"),
        "row_count": int(len(dataframe)),
        "feature_count": len(features),
        "features": features,
        "targets": targets,
    }


def save_reference_baseline(
    baseline: dict[str, Any],
    output_path: Path = DEFAULT_DRIFT_BASELINE_PATH,
) -> None:
    """Persist the drift reference baseline as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(baseline, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def build_and_save_reference_baseline(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    output_path: Path = DEFAULT_DRIFT_BASELINE_PATH,
) -> dict[str, Any]:
    """Build and persist the configured drift reference baseline."""
    baseline = build_reference_baseline_from_config(config_path)
    save_reference_baseline(baseline, output_path)
    return baseline


def _summarize_column(
    dataframe: pd.DataFrame,
    *,
    column_name: str,
    column_rules: dict[str, Any],
) -> dict[str, Any]:
    if column_name not in dataframe.columns:
        raise DriftBaselineError(f"Column missing from dataset: {column_name}")

    dtype = str(column_rules.get("dtype"))
    series = dataframe[column_name]
    common_summary = {
        "dtype": dtype,
        "role": column_rules.get("role"),
        "count": int(len(series)),
        "null_count": int(series.isna().sum()),
        "null_ratio": _rate(int(series.isna().sum()), len(series)),
    }

    if dtype in NUMERIC_DTYPES:
        summary = {
            **common_summary,
            "kind": "numeric",
            "stats": _numeric_stats(series),
        }
        if "allowed_values" in column_rules:
            summary["allowed_values"] = list(column_rules["allowed_values"])
            summary["value_counts"] = _value_counts(series)
            summary["value_ratios"] = _value_ratios(series)
        return summary
    if dtype in CATEGORICAL_DTYPES:
        return {
            **common_summary,
            "kind": "categorical",
            "allowed_values": list(column_rules.get("allowed_values", [])),
            "value_counts": _value_counts(series),
            "value_ratios": _value_ratios(series),
        }

    raise DriftBaselineError(f"Unsupported drift baseline dtype: {dtype}")


def _numeric_stats(series: pd.Series) -> dict[str, float | int | None]:
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


def _columns_by_role(columns: dict[str, Any], role: str) -> list[str]:
    return [
        column_name
        for column_name, column_rules in columns.items()
        if isinstance(column_rules, dict) and column_rules.get("role") == role
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
