"""Build dashboard-ready snapshots from local monitoring reports."""

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from app.observability.drift_baseline import DEFAULT_DRIFT_BASELINE_PATH
from app.observability.drift_comparison import DEFAULT_DATA_DRIFT_SUMMARY_PATH
from app.observability.inference_snapshot import DEFAULT_INFERENCE_SNAPSHOT_PATH
from app.observability.monitoring_alerts import DEFAULT_MONITORING_ALERTS_PATH
from app.observability.monitoring_summary import DEFAULT_MONITORING_SUMMARY_PATH

DEFAULT_DASHBOARD_SNAPSHOT_PATH = Path("reports/monitoring/dashboard_snapshot.json")


class DashboardSnapshotError(ValueError):
    """Raised when a dashboard snapshot cannot be built."""


def load_dashboard_source(path: Path) -> dict[str, Any]:
    """Load one dashboard source report."""
    if not path.is_file():
        raise DashboardSnapshotError(f"Dashboard source file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DashboardSnapshotError(f"Invalid dashboard source JSON: {path}") from exc
    if not isinstance(data, dict):
        raise DashboardSnapshotError(f"Dashboard source must be a JSON object: {path}")
    return data


def build_dashboard_snapshot(
    *,
    prediction_summary: dict[str, Any],
    alerts: dict[str, Any],
    reference_baseline: dict[str, Any],
    inference_snapshot: dict[str, Any],
    data_drift_summary: dict[str, Any],
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build one dashboard-ready JSON snapshot from local reports."""
    active_alerts = [
        alert for alert in alerts.get("alerts", []) if alert.get("status") == "triggered"
    ]
    return {
        "snapshot_version": "v1",
        "generated_at": generated_at or _utc_now(),
        "overall_status": alerts.get("overall_status"),
        "cards": {
            "requests": {
                "request_count": prediction_summary.get("request_count", 0),
                "success_count": prediction_summary.get("success_count", 0),
                "failure_count": prediction_summary.get("failure_count", 0),
                "failure_rate": prediction_summary.get("failure_rate", 0.0),
            },
            "latency": prediction_summary.get("latency_ms", {}),
            "alerts": {
                "overall_status": alerts.get("overall_status"),
                "active_alert_count": alerts.get("active_alert_count", 0),
                "triggered_alert_names": [
                    str(alert.get("name")) for alert in active_alerts
                ],
            },
            "drift": {
                "overall_status": data_drift_summary.get("overall_status"),
                "drifted_feature_count": data_drift_summary.get(
                    "drifted_feature_count",
                    0,
                ),
                "insufficient_feature_count": data_drift_summary.get(
                    "insufficient_feature_count",
                    0,
                ),
                "reference_row_count": data_drift_summary.get("reference_row_count"),
                "inference_row_count": data_drift_summary.get("inference_row_count"),
            },
            "telemetry_quality": {
                "raw_event_count": prediction_summary.get("raw_event_count", 0),
                "skipped_event_count": prediction_summary.get(
                    "skipped_event_count",
                    0,
                ),
                "feature_event_count": inference_snapshot.get("feature_event_count", 0),
            },
        },
        "distributions": {
            "prediction_distribution": prediction_summary.get(
                "prediction_distribution",
                {},
            ),
            "probability_distribution": prediction_summary.get(
                "probability_distribution",
                {},
            ),
            "drifted_features": _drifted_features(data_drift_summary),
        },
        "report_freshness": {
            "prediction_summary_generated_at": prediction_summary.get("generated_at"),
            "alerts_generated_at": alerts.get("generated_at"),
            "reference_baseline_generated_at": reference_baseline.get("generated_at"),
            "inference_snapshot_generated_at": inference_snapshot.get("generated_at"),
            "data_drift_summary_generated_at": data_drift_summary.get("generated_at"),
        },
        "source_reports": {
            "prediction_summary": str(DEFAULT_MONITORING_SUMMARY_PATH),
            "alerts": str(DEFAULT_MONITORING_ALERTS_PATH),
            "reference_baseline": str(DEFAULT_DRIFT_BASELINE_PATH),
            "inference_snapshot": str(DEFAULT_INFERENCE_SNAPSHOT_PATH),
            "data_drift_summary": str(DEFAULT_DATA_DRIFT_SUMMARY_PATH),
        },
    }


def save_dashboard_snapshot(
    snapshot: dict[str, Any],
    output_path: Path = DEFAULT_DASHBOARD_SNAPSHOT_PATH,
) -> None:
    """Persist a dashboard snapshot as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def build_and_save_dashboard_snapshot(
    *,
    prediction_summary_path: Path = DEFAULT_MONITORING_SUMMARY_PATH,
    alerts_path: Path = DEFAULT_MONITORING_ALERTS_PATH,
    reference_baseline_path: Path = DEFAULT_DRIFT_BASELINE_PATH,
    inference_snapshot_path: Path = DEFAULT_INFERENCE_SNAPSHOT_PATH,
    data_drift_summary_path: Path = DEFAULT_DATA_DRIFT_SUMMARY_PATH,
    output_path: Path = DEFAULT_DASHBOARD_SNAPSHOT_PATH,
) -> dict[str, Any]:
    """Load local reports, build a dashboard snapshot, and persist it."""
    snapshot = build_dashboard_snapshot(
        prediction_summary=load_dashboard_source(prediction_summary_path),
        alerts=load_dashboard_source(alerts_path),
        reference_baseline=load_dashboard_source(reference_baseline_path),
        inference_snapshot=load_dashboard_source(inference_snapshot_path),
        data_drift_summary=load_dashboard_source(data_drift_summary_path),
    )
    save_dashboard_snapshot(snapshot, output_path)
    return snapshot


def _drifted_features(data_drift_summary: dict[str, Any]) -> list[str]:
    features = data_drift_summary.get("features")
    if not isinstance(features, dict):
        return []
    return [
        feature_name
        for feature_name, feature in sorted(features.items())
        if isinstance(feature, dict) and feature.get("status") == "drift_detected"
    ]


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
