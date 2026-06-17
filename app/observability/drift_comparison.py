"""Compare reference and inference feature distributions for local drift checks."""

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from app.observability.drift_baseline import DEFAULT_DRIFT_BASELINE_PATH
from app.observability.inference_snapshot import DEFAULT_INFERENCE_SNAPSHOT_PATH

DEFAULT_DATA_DRIFT_SUMMARY_PATH = Path("reports/drift/data_drift_summary.json")
DEFAULT_DRIFT_THRESHOLDS = {
    "numeric_mean_relative_change": 0.2,
    "numeric_range_expansion_ratio": 0.2,
    "categorical_max_ratio_change": 0.2,
}


class DriftComparisonError(ValueError):
    """Raised when local drift comparison cannot be completed."""


def load_drift_json(path: Path) -> dict[str, Any]:
    """Load a drift input JSON file."""
    if not path.is_file():
        raise DriftComparisonError(f"Drift input file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DriftComparisonError(f"Invalid drift JSON: {path}") from exc
    if not isinstance(data, dict):
        raise DriftComparisonError(f"Drift input must be a JSON object: {path}")
    return data


def compare_data_drift(
    reference_baseline: dict[str, Any],
    inference_snapshot: dict[str, Any],
    *,
    thresholds: dict[str, float] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Compare reference baseline and inference snapshot feature summaries."""
    resolved_thresholds = {**DEFAULT_DRIFT_THRESHOLDS, **(thresholds or {})}
    reference_features = _features(reference_baseline, "reference")
    inference_features = _features(inference_snapshot, "inference")
    row_count = int(inference_snapshot.get("row_count") or 0)

    compared_features = {}
    for feature_name, reference_feature in reference_features.items():
        inference_feature = inference_features.get(feature_name)
        if inference_feature is None:
            if row_count == 0:
                compared_features[feature_name] = _insufficient_feature_result(
                    feature_name,
                    reference_feature,
                    {},
                )
            else:
                compared_features[feature_name] = _missing_feature_result(
                    feature_name,
                    reference_feature,
                )
            continue
        compared_features[feature_name] = _compare_feature(
            feature_name,
            reference_feature,
            inference_feature,
            thresholds=resolved_thresholds,
            inference_row_count=row_count,
        )

    drifted_features = [
        name
        for name, result in compared_features.items()
        if result["status"] == "drift_detected"
    ]
    insufficient_features = [
        name
        for name, result in compared_features.items()
        if result["status"] == "insufficient_data"
    ]

    if row_count == 0:
        overall_status = "insufficient_data"
    elif drifted_features:
        overall_status = "drift_detected"
    else:
        overall_status = "ok"

    return {
        "summary_version": "v1",
        "generated_at": generated_at or _utc_now(),
        "reference_generated_at": reference_baseline.get("generated_at"),
        "inference_generated_at": inference_snapshot.get("generated_at"),
        "schema_name": reference_baseline.get("schema_name"),
        "schema_version": reference_baseline.get("schema_version"),
        "reference_row_count": reference_baseline.get("row_count"),
        "inference_row_count": row_count,
        "overall_status": overall_status,
        "feature_count": len(compared_features),
        "drifted_feature_count": len(drifted_features),
        "insufficient_feature_count": len(insufficient_features),
        "thresholds": resolved_thresholds,
        "features": compared_features,
    }


def save_data_drift_summary(
    summary: dict[str, Any],
    output_path: Path = DEFAULT_DATA_DRIFT_SUMMARY_PATH,
) -> None:
    """Persist a local data drift summary as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def build_and_save_data_drift_summary(
    *,
    reference_path: Path = DEFAULT_DRIFT_BASELINE_PATH,
    inference_path: Path = DEFAULT_INFERENCE_SNAPSHOT_PATH,
    output_path: Path = DEFAULT_DATA_DRIFT_SUMMARY_PATH,
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Load drift inputs, compare them, and persist the summary."""
    reference_baseline = load_drift_json(reference_path)
    inference_snapshot = load_drift_json(inference_path)
    summary = compare_data_drift(
        reference_baseline,
        inference_snapshot,
        thresholds=thresholds,
    )
    save_data_drift_summary(summary, output_path)
    return summary


def _compare_feature(
    feature_name: str,
    reference_feature: dict[str, Any],
    inference_feature: dict[str, Any],
    *,
    thresholds: dict[str, float],
    inference_row_count: int,
) -> dict[str, Any]:
    if inference_row_count == 0:
        return _insufficient_feature_result(reference_feature, inference_feature)

    if reference_feature.get("kind") == "numeric":
        return _compare_numeric_feature(
            feature_name,
            reference_feature,
            inference_feature,
            thresholds=thresholds,
        )
    return _compare_categorical_feature(
        feature_name,
        reference_feature,
        inference_feature,
        thresholds=thresholds,
    )


def _compare_numeric_feature(
    feature_name: str,
    reference_feature: dict[str, Any],
    inference_feature: dict[str, Any],
    *,
    thresholds: dict[str, float],
) -> dict[str, Any]:
    reference_stats = reference_feature.get("stats", {})
    inference_stats = inference_feature.get("stats", {})
    reference_mean = _number(reference_stats.get("mean"))
    inference_mean = _number(inference_stats.get("mean"))
    mean_relative_change = _relative_change(reference_mean, inference_mean)
    reference_min = _number(reference_stats.get("min"))
    reference_max = _number(reference_stats.get("max"))
    inference_min = _number(inference_stats.get("min"))
    inference_max = _number(inference_stats.get("max"))
    range_expansion_ratio = _range_expansion_ratio(
        reference_min,
        reference_max,
        inference_min,
        inference_max,
    )
    checks = {
        "mean_relative_change": mean_relative_change,
        "range_expansion_ratio": range_expansion_ratio,
    }
    status = "drift_detected" if (
        mean_relative_change > thresholds["numeric_mean_relative_change"]
        or range_expansion_ratio > thresholds["numeric_range_expansion_ratio"]
    ) else "ok"
    return {
        "feature_name": feature_name,
        "kind": "numeric",
        "status": status,
        "reference_count": reference_feature.get("count"),
        "inference_count": inference_feature.get("count"),
        "checks": checks,
    }


def _compare_categorical_feature(
    feature_name: str,
    reference_feature: dict[str, Any],
    inference_feature: dict[str, Any],
    *,
    thresholds: dict[str, float],
) -> dict[str, Any]:
    reference_ratios = reference_feature.get("value_ratios", {})
    inference_ratios = inference_feature.get("value_ratios", {})
    categories = sorted(set(reference_ratios) | set(inference_ratios))
    ratio_changes = {
        category: round(
            abs(
                float(inference_ratios.get(category, 0.0))
                - float(reference_ratios.get(category, 0.0))
            ),
            6,
        )
        for category in categories
    }
    max_ratio_change = max(ratio_changes.values(), default=0.0)
    status = (
        "drift_detected"
        if max_ratio_change > thresholds["categorical_max_ratio_change"]
        else "ok"
    )
    return {
        "feature_name": feature_name,
        "kind": "categorical",
        "status": status,
        "reference_count": reference_feature.get("count"),
        "inference_count": inference_feature.get("count"),
        "checks": {
            "max_ratio_change": max_ratio_change,
            "ratio_changes": ratio_changes,
        },
    }


def _missing_feature_result(
    feature_name: str,
    reference_feature: dict[str, Any],
) -> dict[str, Any]:
    return {
        "feature_name": feature_name,
        "kind": reference_feature.get("kind"),
        "status": "insufficient_data",
        "reference_count": reference_feature.get("count"),
        "inference_count": 0,
        "checks": {"reason": "feature_missing_from_inference_snapshot"},
    }


def _insufficient_feature_result(
    feature_name: str,
    reference_feature: dict[str, Any],
    inference_feature: dict[str, Any],
) -> dict[str, Any]:
    return {
        "feature_name": feature_name,
        "kind": reference_feature.get("kind"),
        "status": "insufficient_data",
        "reference_count": reference_feature.get("count"),
        "inference_count": inference_feature.get("count", 0),
        "checks": {"reason": "no_inference_rows"},
    }


def _features(data: dict[str, Any], label: str) -> dict[str, Any]:
    features = data.get("features")
    if not isinstance(features, dict):
        raise DriftComparisonError(f"{label} input must contain features.")
    return features


def _number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _relative_change(reference: float | None, current: float | None) -> float:
    if reference is None or current is None:
        return 0.0
    if reference == 0:
        return 0.0 if current == 0 else 1.0
    return round(abs(current - reference) / abs(reference), 6)


def _range_expansion_ratio(
    reference_min: float | None,
    reference_max: float | None,
    inference_min: float | None,
    inference_max: float | None,
) -> float:
    if None in {reference_min, reference_max, inference_min, inference_max}:
        return 0.0
    reference_range = max(reference_max - reference_min, 0.0)
    below = max(reference_min - inference_min, 0.0)
    above = max(inference_max - reference_max, 0.0)
    if reference_range == 0:
        return 0.0 if below == 0 and above == 0 else 1.0
    return round((below + above) / reference_range, 6)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
