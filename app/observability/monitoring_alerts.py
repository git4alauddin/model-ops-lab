"""Evaluate local alert rules from prediction monitoring summaries."""

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from app.observability.monitoring_summary import DEFAULT_MONITORING_SUMMARY_PATH

DEFAULT_MONITORING_ALERTS_PATH = Path("reports/monitoring/alerts.json")
DEFAULT_ALERT_THRESHOLDS = {
    "minimum_request_count": 1,
    "max_failure_rate": 0.2,
    "max_p95_latency_ms": 1000.0,
    "max_skipped_event_ratio": 0.1,
    "max_prediction_class_share": 0.95,
}


class MonitoringAlertsError(ValueError):
    """Raised when monitoring alerts cannot be evaluated."""


def load_prediction_monitoring_summary(summary_path: Path) -> dict[str, Any]:
    """Load a prediction monitoring summary JSON file."""
    if not summary_path.is_file():
        raise MonitoringAlertsError(f"Monitoring summary file not found: {summary_path}")

    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MonitoringAlertsError(
            f"Invalid monitoring summary JSON: {summary_path}"
        ) from exc
    if not isinstance(summary, dict):
        raise MonitoringAlertsError("Monitoring summary must be a JSON object.")
    return summary


def evaluate_prediction_monitoring_alerts(
    summary: dict[str, Any],
    *,
    thresholds: dict[str, float | int] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Evaluate local alert rules from a prediction monitoring summary."""
    resolved_thresholds = {**DEFAULT_ALERT_THRESHOLDS, **(thresholds or {})}
    alerts = [
        _missing_telemetry_alert(summary, resolved_thresholds),
        _failure_rate_alert(summary, resolved_thresholds),
        _p95_latency_alert(summary, resolved_thresholds),
        _skipped_event_ratio_alert(summary, resolved_thresholds),
        _prediction_collapse_alert(summary, resolved_thresholds),
    ]
    active_alerts = [alert for alert in alerts if alert["status"] == "triggered"]

    return {
        "generated_at": generated_at or _utc_now(),
        "source_path": summary.get("source_path"),
        "summary_generated_at": summary.get("generated_at"),
        "overall_status": "alerting" if active_alerts else "ok",
        "active_alert_count": len(active_alerts),
        "thresholds": resolved_thresholds,
        "alerts": alerts,
    }


def save_monitoring_alerts(
    alert_report: dict[str, Any],
    output_path: Path = DEFAULT_MONITORING_ALERTS_PATH,
) -> None:
    """Persist a monitoring alert report as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(alert_report, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def build_and_save_monitoring_alerts(
    *,
    summary_path: Path = DEFAULT_MONITORING_SUMMARY_PATH,
    output_path: Path = DEFAULT_MONITORING_ALERTS_PATH,
    thresholds: dict[str, float | int] | None = None,
) -> dict[str, Any]:
    """Load a prediction summary, evaluate alerts, and persist the report."""
    summary = load_prediction_monitoring_summary(summary_path)
    alert_report = evaluate_prediction_monitoring_alerts(
        summary,
        thresholds=thresholds,
    )
    save_monitoring_alerts(alert_report, output_path)
    return alert_report


def _missing_telemetry_alert(
    summary: dict[str, Any],
    thresholds: dict[str, float | int],
) -> dict[str, Any]:
    request_count = _number(summary.get("request_count"), default=0)
    threshold = thresholds["minimum_request_count"]
    return _alert(
        name="missing_prediction_telemetry",
        status="triggered" if request_count < threshold else "ok",
        severity="critical",
        metric_value=request_count,
        threshold=threshold,
        message="Supported prediction telemetry count is below the local threshold.",
        recommended_action=(
            "Generate prediction telemetry before relying on monitoring signals."
        ),
    )


def _failure_rate_alert(
    summary: dict[str, Any],
    thresholds: dict[str, float | int],
) -> dict[str, Any]:
    failure_rate = _number(summary.get("failure_rate"), default=0.0)
    threshold = thresholds["max_failure_rate"]
    return _alert(
        name="high_failure_rate",
        status="triggered" if failure_rate > threshold else "ok",
        severity="critical",
        metric_value=failure_rate,
        threshold=threshold,
        message="Prediction failure rate is above the local alert threshold.",
        recommended_action=(
            "Inspect failure_categories and recent serving logs before deploying."
        ),
    )


def _p95_latency_alert(
    summary: dict[str, Any],
    thresholds: dict[str, float | int],
) -> dict[str, Any]:
    latency = summary.get("latency_ms")
    p95_latency = None
    if isinstance(latency, dict):
        p95_latency = latency.get("p95")
    metric_value = _number(p95_latency, default=0.0)
    threshold = thresholds["max_p95_latency_ms"]
    return _alert(
        name="high_p95_latency",
        status="triggered" if metric_value > threshold else "ok",
        severity="warning",
        metric_value=metric_value,
        threshold=threshold,
        message="p95 latency is above the local alert threshold.",
        recommended_action="Inspect model loading and prediction latency.",
    )


def _skipped_event_ratio_alert(
    summary: dict[str, Any],
    thresholds: dict[str, float | int],
) -> dict[str, Any]:
    raw_event_count = _number(summary.get("raw_event_count"), default=0)
    skipped_event_count = _number(summary.get("skipped_event_count"), default=0)
    skipped_ratio = _rate(skipped_event_count, raw_event_count)
    threshold = thresholds["max_skipped_event_ratio"]
    return _alert(
        name="high_skipped_event_ratio",
        status="triggered" if skipped_ratio > threshold else "ok",
        severity="warning",
        metric_value=skipped_ratio,
        threshold=threshold,
        message="Too many telemetry records were skipped by the V9 filter.",
        recommended_action=(
            "Inspect skipped_events and consider starting a fresh telemetry window."
        ),
    )


def _prediction_collapse_alert(
    summary: dict[str, Any],
    thresholds: dict[str, float | int],
) -> dict[str, Any]:
    distribution = summary.get("prediction_distribution")
    prediction_count = 0
    max_class_share = 0.0
    if isinstance(distribution, dict):
        counts = [_number(value, default=0) for value in distribution.values()]
        prediction_count = int(sum(counts))
        if prediction_count:
            max_class_share = max(counts) / prediction_count

    threshold = thresholds["max_prediction_class_share"]
    triggered = prediction_count > 0 and max_class_share > threshold
    return _alert(
        name="prediction_distribution_collapse",
        status="triggered" if triggered else "ok",
        severity="warning",
        metric_value=round(max_class_share, 6),
        threshold=threshold,
        message="One prediction class dominates the local telemetry window.",
        recommended_action=(
            "Inspect prediction_distribution and compare against expected traffic."
        ),
    )


def _alert(
    *,
    name: str,
    status: str,
    severity: str,
    metric_value: float | int,
    threshold: float | int,
    message: str,
    recommended_action: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "severity": severity,
        "metric_value": metric_value,
        "threshold": threshold,
        "message": message,
        "recommended_action": recommended_action,
    }


def _number(value: Any, *, default: float | int) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return float(default)


def _rate(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
