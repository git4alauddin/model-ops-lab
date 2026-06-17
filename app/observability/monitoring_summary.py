"""Build local monitoring summaries from prediction telemetry."""

from collections import Counter
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

DEFAULT_PREDICTION_TELEMETRY_PATH = Path("logs/predictions.jsonl")
DEFAULT_MONITORING_SUMMARY_PATH = Path("reports/monitoring/prediction_summary.json")
SUPPORTED_EVENT_VERSION = "v1"
SUPPORTED_EVENT_TYPES = {
    "prediction_success",
    "prediction_failure",
    "prediction_validation_failure",
}
PROBABILITY_BUCKETS = (
    (0.0, 0.2),
    (0.2, 0.4),
    (0.4, 0.6),
    (0.6, 0.8),
    (0.8, 1.0),
)


class MonitoringSummaryError(ValueError):
    """Raised when prediction telemetry cannot be summarized."""


def load_prediction_telemetry(log_path: Path) -> list[dict[str, Any]]:
    """Load prediction telemetry events from a JSONL file."""
    if not log_path.is_file():
        raise MonitoringSummaryError(f"Prediction telemetry file not found: {log_path}")

    events = []
    lines = log_path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise MonitoringSummaryError(
                f"Invalid JSON telemetry at {log_path}:{line_number}"
            ) from exc
        if not isinstance(event, dict):
            raise MonitoringSummaryError(
                f"Telemetry event must be a JSON object at {log_path}:{line_number}"
            )
        events.append(event)

    if not events:
        raise MonitoringSummaryError(f"No prediction telemetry events found: {log_path}")
    return events


def build_prediction_monitoring_summary(
    events: list[dict[str, Any]],
    *,
    source_path: Path = DEFAULT_PREDICTION_TELEMETRY_PATH,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a compact monitoring summary from prediction telemetry events."""
    if not events:
        raise MonitoringSummaryError("No prediction telemetry events provided.")

    valid_events, skipped_events = _filter_supported_events(events)
    if not valid_events:
        raise MonitoringSummaryError("No supported V9 prediction telemetry events found.")

    event_counts = Counter(str(event.get("event_type")) for event in valid_events)
    status_counts = Counter(str(event.get("status")) for event in valid_events)
    failure_categories = Counter(
        str(event["error_category"])
        for event in valid_events
        if event.get("error_category") is not None
    )
    endpoints = Counter(str(event.get("endpoint")) for event in valid_events)
    model_versions = Counter(
        str(event["model_version"])
        for event in valid_events
        if event.get("model_version") is not None
    )
    deployment_versions = Counter(
        str(event["deployment_version"])
        for event in valid_events
        if event.get("deployment_version") is not None
    )

    success_events = [
        event for event in valid_events if event.get("status") == "success"
    ]
    failed_events = [event for event in valid_events if event.get("status") == "failed"]
    latencies = _numeric_values(event.get("latency_ms") for event in success_events)
    probabilities = _numeric_values(event.get("probability") for event in success_events)
    predictions = [
        str(event["prediction"])
        for event in success_events
        if event.get("prediction") is not None
    ]

    return {
        "generated_at": generated_at or _utc_now(),
        "source_path": str(source_path),
        "total_events": len(valid_events),
        "raw_event_count": len(events),
        "skipped_event_count": len(skipped_events),
        "skipped_events": dict(sorted(Counter(skipped_events).items())),
        "event_counts": dict(sorted(event_counts.items())),
        "status_counts": dict(sorted(status_counts.items())),
        "request_count": len(valid_events),
        "success_count": len(success_events),
        "failure_count": len(failed_events),
        "failure_rate": _rate(len(failed_events), len(valid_events)),
        "endpoints": dict(sorted(endpoints.items())),
        "model_versions": dict(sorted(model_versions.items())),
        "deployment_versions": dict(sorted(deployment_versions.items())),
        "failure_categories": dict(sorted(failure_categories.items())),
        "latency_ms": _latency_summary(latencies),
        "prediction_distribution": dict(sorted(Counter(predictions).items())),
        "probability_distribution": _probability_distribution(probabilities),
    }


def _filter_supported_events(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    valid_events = []
    skipped_events = []

    for event in events:
        event_version = event.get("event_version")
        event_type = event.get("event_type")
        if event_version is None:
            skipped_events.append("missing_event_version")
            continue
        if event_version != SUPPORTED_EVENT_VERSION:
            skipped_events.append("unsupported_event_version")
            continue
        if event_type is None:
            skipped_events.append("missing_event_type")
            continue
        if event_type not in SUPPORTED_EVENT_TYPES:
            skipped_events.append("unsupported_event_type")
            continue
        valid_events.append(event)

    return valid_events, skipped_events


def save_prediction_monitoring_summary(
    summary: dict[str, Any],
    output_path: Path = DEFAULT_MONITORING_SUMMARY_PATH,
) -> None:
    """Persist a prediction monitoring summary as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def build_and_save_prediction_monitoring_summary(
    *,
    log_path: Path = DEFAULT_PREDICTION_TELEMETRY_PATH,
    output_path: Path = DEFAULT_MONITORING_SUMMARY_PATH,
) -> dict[str, Any]:
    """Load prediction telemetry, build a summary, and persist it."""
    events = load_prediction_telemetry(log_path)
    summary = build_prediction_monitoring_summary(events, source_path=log_path)
    save_prediction_monitoring_summary(summary, output_path)
    return summary


def _latency_summary(latencies: list[float]) -> dict[str, float | int | None]:
    if not latencies:
        return {
            "count": 0,
            "average": None,
            "p95": None,
            "p99": None,
            "min": None,
            "max": None,
        }

    sorted_latencies = sorted(latencies)
    return {
        "count": len(sorted_latencies),
        "average": round(sum(sorted_latencies) / len(sorted_latencies), 6),
        "p95": _nearest_rank_percentile(sorted_latencies, 95),
        "p99": _nearest_rank_percentile(sorted_latencies, 99),
        "min": sorted_latencies[0],
        "max": sorted_latencies[-1],
    }


def _probability_distribution(probabilities: list[float]) -> dict[str, Any]:
    buckets = {f"{lower:.1f}-{upper:.1f}": 0 for lower, upper in PROBABILITY_BUCKETS}
    for probability in probabilities:
        bucket = _probability_bucket(probability)
        buckets[bucket] += 1

    if not probabilities:
        return {
            "count": 0,
            "average": None,
            "min": None,
            "max": None,
            "buckets": buckets,
        }

    return {
        "count": len(probabilities),
        "average": round(sum(probabilities) / len(probabilities), 6),
        "min": min(probabilities),
        "max": max(probabilities),
        "buckets": buckets,
    }


def _probability_bucket(probability: float) -> str:
    for lower, upper in PROBABILITY_BUCKETS:
        if lower <= probability < upper:
            return f"{lower:.1f}-{upper:.1f}"
    if probability == 1.0:
        return "0.8-1.0"
    raise MonitoringSummaryError(f"Probability out of range: {probability}")


def _numeric_values(values) -> list[float]:
    numeric_values = []
    for value in values:
        if isinstance(value, (int, float)):
            numeric_values.append(float(value))
    return numeric_values


def _nearest_rank_percentile(sorted_values: list[float], percentile: int) -> float:
    rank = _ceil(percentile / 100 * len(sorted_values))
    index = max(0, min(len(sorted_values) - 1, rank - 1))
    return sorted_values[index]


def _ceil(value: float) -> int:
    integer = int(value)
    if value == integer:
        return integer
    return integer + 1


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
