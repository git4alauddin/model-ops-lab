"""Prometheus metrics rendering for local monitoring reports."""

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from prometheus_client import CollectorRegistry, Gauge, generate_latest

from app.observability.drift_comparison import DEFAULT_DATA_DRIFT_SUMMARY_PATH
from app.observability.monitoring_alerts import DEFAULT_MONITORING_ALERTS_PATH
from app.observability.monitoring_summary import DEFAULT_MONITORING_SUMMARY_PATH


class PrometheusMetricsError(ValueError):
    """Raised when Prometheus metrics cannot be rendered."""


def load_prometheus_source(path: Path) -> dict[str, Any]:
    """Load one local report used by Prometheus metrics."""
    if not path.is_file():
        raise PrometheusMetricsError(f"Prometheus source file not found: {path}")
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PrometheusMetricsError(f"Invalid Prometheus source JSON: {path}") from exc
    if not isinstance(report, dict):
        raise PrometheusMetricsError("Prometheus source report must be a JSON object.")
    return report


def build_prometheus_metrics_from_reports(
    *,
    prediction_summary_path: Path = DEFAULT_MONITORING_SUMMARY_PATH,
    alerts_path: Path = DEFAULT_MONITORING_ALERTS_PATH,
    data_drift_summary_path: Path = DEFAULT_DATA_DRIFT_SUMMARY_PATH,
) -> bytes:
    """Load available local monitoring reports and render Prometheus metrics."""
    prediction_summary = _load_optional_source(prediction_summary_path)
    alerts = _load_optional_source(alerts_path)
    data_drift_summary = _load_optional_source(data_drift_summary_path)
    return render_prometheus_metrics(
        prediction_summary=prediction_summary,
        alerts=alerts,
        data_drift_summary=data_drift_summary,
    )


def render_prometheus_metrics(
    *,
    prediction_summary: dict[str, Any] | None = None,
    alerts: dict[str, Any] | None = None,
    data_drift_summary: dict[str, Any] | None = None,
    generated_at: str | None = None,
) -> bytes:
    """Render Prometheus text exposition bytes from local monitoring reports."""
    registry = CollectorRegistry()
    _build_info(registry, generated_at=generated_at)
    _report_availability(
        registry,
        prediction_summary=prediction_summary,
        alerts=alerts,
        data_drift_summary=data_drift_summary,
    )
    _prediction_metrics(registry, prediction_summary or {})
    _alert_metrics(registry, alerts or {})
    _drift_metrics(registry, data_drift_summary or {})
    return generate_latest(registry)


def _build_info(registry: CollectorRegistry, *, generated_at: str | None) -> None:
    gauge = Gauge(
        "modelopslab_monitoring_build_info",
        "Local monitoring metrics build marker.",
        ["generated_at"],
        registry=registry,
    )
    gauge.labels(generated_at=generated_at or datetime.now(UTC).isoformat()).set(1)


def _report_availability(
    registry: CollectorRegistry,
    *,
    prediction_summary: dict[str, Any] | None,
    alerts: dict[str, Any] | None,
    data_drift_summary: dict[str, Any] | None,
) -> None:
    gauge = Gauge(
        "modelopslab_monitoring_report_available",
        "Whether a local monitoring report was available.",
        ["report"],
        registry=registry,
    )
    gauge.labels(report="prediction_summary").set(1 if prediction_summary else 0)
    gauge.labels(report="alerts").set(1 if alerts else 0)
    gauge.labels(report="data_drift_summary").set(1 if data_drift_summary else 0)


def _prediction_metrics(
    registry: CollectorRegistry,
    summary: dict[str, Any],
) -> None:
    _gauge(
        registry,
        "modelopslab_prediction_requests",
        "Supported V9 prediction telemetry requests.",
    ).set(_number(summary.get("request_count")))
    _gauge(
        registry,
        "modelopslab_prediction_successes",
        "Successful prediction telemetry events.",
    ).set(_number(summary.get("success_count")))
    _gauge(
        registry,
        "modelopslab_prediction_failures",
        "Failed prediction telemetry events.",
    ).set(_number(summary.get("failure_count")))
    _gauge(
        registry,
        "modelopslab_prediction_failure_rate",
        "Local prediction failure rate.",
    ).set(_number(summary.get("failure_rate")))

    latency = summary.get("latency_ms")
    if not isinstance(latency, dict):
        latency = {}
    latency_gauge = Gauge(
        "modelopslab_prediction_latency_ms",
        "Local successful prediction latency by statistic.",
        ["stat"],
        registry=registry,
    )
    for stat in ("average", "p95", "p99", "min", "max"):
        latency_gauge.labels(stat=stat).set(_number(latency.get(stat)))

    telemetry_gauge = Gauge(
        "modelopslab_telemetry_events",
        "Local telemetry events by processing state.",
        ["state"],
        registry=registry,
    )
    telemetry_gauge.labels(state="raw").set(_number(summary.get("raw_event_count")))
    telemetry_gauge.labels(state="skipped").set(
        _number(summary.get("skipped_event_count"))
    )


def _alert_metrics(registry: CollectorRegistry, alerts: dict[str, Any]) -> None:
    _gauge(
        registry,
        "modelopslab_monitoring_active_alerts",
        "Local active monitoring alert count.",
    ).set(_number(alerts.get("active_alert_count")))

    overall_status = str(alerts.get("overall_status", "unknown"))
    status_gauge = Gauge(
        "modelopslab_monitoring_status",
        "Local monitoring status flag by status.",
        ["status"],
        registry=registry,
    )
    for status in ("ok", "alerting", "unknown"):
        status_gauge.labels(status=status).set(1 if overall_status == status else 0)


def _drift_metrics(registry: CollectorRegistry, summary: dict[str, Any]) -> None:
    overall_status = str(summary.get("overall_status", "unknown"))
    _gauge(
        registry,
        "modelopslab_data_drift_detected",
        "Whether local data drift was detected.",
    ).set(1 if overall_status == "drift_detected" else 0)
    _gauge(
        registry,
        "modelopslab_data_drifted_features",
        "Local drifted feature count.",
    ).set(_number(summary.get("drifted_feature_count")))
    _gauge(
        registry,
        "modelopslab_data_drift_inference_rows",
        "Local inference row count used for drift comparison.",
    ).set(_number(summary.get("inference_row_count")))


def _gauge(
    registry: CollectorRegistry,
    name: str,
    documentation: str,
) -> Gauge:
    return Gauge(name, documentation, registry=registry)


def _load_optional_source(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return load_prometheus_source(path)


def _number(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0
