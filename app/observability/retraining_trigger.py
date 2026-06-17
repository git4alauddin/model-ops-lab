"""Evaluate local retraining trigger decisions from monitoring reports."""

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from app.observability.drift_comparison import DEFAULT_DATA_DRIFT_SUMMARY_PATH
from app.observability.monitoring_alerts import DEFAULT_MONITORING_ALERTS_PATH

DEFAULT_RETRAINING_TRIGGER_DECISION_PATH = Path(
    "reports/retraining/retraining_trigger_decision.json"
)
DEFAULT_RETRAINING_TRIGGER_THRESHOLDS = {
    "minimum_request_count": 1,
    "minimum_drift_inference_rows": 1,
}
RETRAINING_RECOMMENDED = "retraining_recommended"
RETRAINING_NOT_REQUIRED = "retraining_not_required"
INSUFFICIENT_MONITORING_DATA = "insufficient_monitoring_data"


class RetrainingTriggerError(ValueError):
    """Raised when retraining trigger evaluation cannot be completed."""


def load_retraining_source(path: Path) -> dict[str, Any]:
    """Load a retraining trigger source report."""
    if not path.is_file():
        raise RetrainingTriggerError(f"Retraining source file not found: {path}")

    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RetrainingTriggerError(f"Invalid retraining source JSON: {path}") from exc

    if not isinstance(report, dict):
        raise RetrainingTriggerError("Retraining source report must be a JSON object.")
    return report


def evaluate_retraining_trigger(
    *,
    alert_report: dict[str, Any] | None,
    drift_summary: dict[str, Any] | None,
    thresholds: dict[str, float | int] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Evaluate whether local monitoring signals recommend retraining."""
    resolved_thresholds = {
        **DEFAULT_RETRAINING_TRIGGER_THRESHOLDS,
        **(thresholds or {}),
    }
    reasons = _trigger_reasons(alert_report, drift_summary, resolved_thresholds)
    blocking_reasons = [
        reason for reason in reasons if reason["category"] == "insufficient_data"
    ]
    recommending_reasons = [
        reason for reason in reasons if reason["category"] == "retraining_signal"
    ]

    if blocking_reasons:
        decision = INSUFFICIENT_MONITORING_DATA
        recommendation = (
            "Regenerate monitoring and drift reports before starting retraining."
        )
    elif recommending_reasons:
        decision = RETRAINING_RECOMMENDED
        recommendation = (
            "Start a governed candidate retraining run, then compare against the "
            "current production model before promotion."
        )
    else:
        decision = RETRAINING_NOT_REQUIRED
        recommendation = (
            "Do not retrain from current local signals. Continue monitoring."
        )

    return {
        "generated_at": generated_at or _utc_now(),
        "decision": decision,
        "recommendation": recommendation,
        "reason_count": len(reasons),
        "reasons": reasons,
        "thresholds": resolved_thresholds,
        "source_reports": {
            "alerts": str(DEFAULT_MONITORING_ALERTS_PATH),
            "data_drift_summary": str(DEFAULT_DATA_DRIFT_SUMMARY_PATH),
        },
        "source_freshness": {
            "alerts_generated_at": (
                alert_report.get("generated_at") if alert_report else None
            ),
            "data_drift_summary_generated_at": (
                drift_summary.get("generated_at") if drift_summary else None
            ),
        },
    }


def save_retraining_trigger_decision(
    decision_report: dict[str, Any],
    output_path: Path = DEFAULT_RETRAINING_TRIGGER_DECISION_PATH,
) -> None:
    """Persist a retraining trigger decision report as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(decision_report, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def build_and_save_retraining_trigger_decision(
    *,
    alerts_path: Path = DEFAULT_MONITORING_ALERTS_PATH,
    drift_summary_path: Path = DEFAULT_DATA_DRIFT_SUMMARY_PATH,
    output_path: Path = DEFAULT_RETRAINING_TRIGGER_DECISION_PATH,
    thresholds: dict[str, float | int] | None = None,
) -> dict[str, Any]:
    """Load monitoring reports, evaluate retraining trigger, and persist it."""
    alert_report = load_retraining_source(alerts_path)
    drift_summary = load_retraining_source(drift_summary_path)
    decision_report = evaluate_retraining_trigger(
        alert_report=alert_report,
        drift_summary=drift_summary,
        thresholds=thresholds,
    )
    save_retraining_trigger_decision(decision_report, output_path)
    return decision_report


def _trigger_reasons(
    alert_report: dict[str, Any] | None,
    drift_summary: dict[str, Any] | None,
    thresholds: dict[str, float | int],
) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    reasons.extend(_alert_trigger_reasons(alert_report, thresholds))
    reasons.extend(_drift_trigger_reasons(drift_summary, thresholds))
    return reasons


def _alert_trigger_reasons(
    alert_report: dict[str, Any] | None,
    thresholds: dict[str, float | int],
) -> list[dict[str, Any]]:
    if alert_report is None:
        return [
            _reason(
                name="missing_monitoring_alert_report",
                category="insufficient_data",
                severity="critical",
                source="alerts",
                message="Monitoring alert report is missing.",
                recommended_action="Build reports/monitoring/alerts.json first.",
            )
        ]

    alerts = alert_report.get("alerts")
    if not isinstance(alerts, list):
        return [
            _reason(
                name="invalid_monitoring_alert_report",
                category="insufficient_data",
                severity="critical",
                source="alerts",
                message="Monitoring alert report does not contain an alerts list.",
                recommended_action="Rebuild the monitoring alert report.",
            )
        ]

    active_alerts = [
        alert for alert in alerts if isinstance(alert, dict) and alert.get("status") == "triggered"
    ]
    reasons = []
    for alert in active_alerts:
        name = str(alert.get("name", "unknown_alert"))
        if name == "missing_prediction_telemetry":
            reasons.append(
                _reason_from_alert(
                    alert,
                    category="insufficient_data",
                    message="Prediction telemetry is missing or below threshold.",
                    recommended_action=(
                        "Generate fresh prediction telemetry before retraining."
                    ),
                )
            )
        elif name in {
            "high_failure_rate",
            "prediction_distribution_collapse",
            "data_drift_detected",
        }:
            reasons.append(
                _reason_from_alert(
                    alert,
                    category="retraining_signal",
                    message=_alert_trigger_message(name),
                    recommended_action=(
                        "Consider a governed retraining run and compare the "
                        "candidate model against production."
                    ),
                )
            )
        elif name == "data_drift_insufficient_data":
            reasons.append(
                _reason_from_alert(
                    alert,
                    category="insufficient_data",
                    message="Data drift report does not have enough inference rows.",
                    recommended_action=(
                        "Generate fresh feature-bearing telemetry before retraining."
                    ),
                )
            )

    request_count = _number(alert_report.get("request_count"), default=None)
    if request_count is not None and request_count < thresholds["minimum_request_count"]:
        reasons.append(
            _reason(
                name="insufficient_request_count",
                category="insufficient_data",
                severity="warning",
                source="alerts",
                metric_value=request_count,
                threshold=thresholds["minimum_request_count"],
                message="Monitoring alert report has too few requests.",
                recommended_action="Generate more prediction traffic first.",
            )
        )
    return reasons


def _drift_trigger_reasons(
    drift_summary: dict[str, Any] | None,
    thresholds: dict[str, float | int],
) -> list[dict[str, Any]]:
    if drift_summary is None:
        return [
            _reason(
                name="missing_data_drift_summary",
                category="insufficient_data",
                severity="critical",
                source="data_drift_summary",
                message="Data drift summary is missing.",
                recommended_action="Build reports/drift/data_drift_summary.json first.",
            )
        ]

    status = drift_summary.get("overall_status")
    inference_row_count = _number(drift_summary.get("inference_row_count"), default=0)
    drifted_feature_count = _number(
        drift_summary.get("drifted_feature_count"),
        default=0,
    )
    if status == "insufficient_data" or (
        inference_row_count < thresholds["minimum_drift_inference_rows"]
    ):
        return [
            _reason(
                name="insufficient_drift_data",
                category="insufficient_data",
                severity="warning",
                source="data_drift_summary",
                metric_value=inference_row_count,
                threshold=thresholds["minimum_drift_inference_rows"],
                message="Data drift summary has insufficient inference rows.",
                recommended_action=(
                    "Generate fresh feature-bearing telemetry and rebuild drift reports."
                ),
            )
        ]

    if status == "drift_detected":
        return [
            _reason(
                name="data_drift_detected",
                category="retraining_signal",
                severity="warning",
                source="data_drift_summary",
                metric_value=drifted_feature_count,
                threshold=0,
                message="Data drift summary detected drifted features.",
                recommended_action=(
                    "Review drifted features and consider candidate retraining."
                ),
            )
        ]

    return []


def _reason_from_alert(
    alert: dict[str, Any],
    *,
    category: str,
    message: str,
    recommended_action: str,
) -> dict[str, Any]:
    return _reason(
        name=str(alert.get("name", "unknown_alert")),
        category=category,
        severity=str(alert.get("severity", "warning")),
        source="alerts",
        metric_value=alert.get("metric_value"),
        threshold=alert.get("threshold"),
        message=message,
        recommended_action=recommended_action,
    )


def _alert_trigger_message(alert_name: str) -> str:
    messages = {
        "high_failure_rate": "Prediction failure rate is high enough to review retraining.",
        "prediction_distribution_collapse": (
            "Prediction distribution collapse may indicate model behavior degradation."
        ),
        "data_drift_detected": "Monitoring alerts include a triggered data drift alert.",
    }
    return messages[alert_name]


def _reason(
    *,
    name: str,
    category: str,
    severity: str,
    source: str,
    message: str,
    recommended_action: str,
    metric_value: Any | None = None,
    threshold: Any | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "category": category,
        "severity": severity,
        "source": source,
        "metric_value": metric_value,
        "threshold": threshold,
        "message": message,
        "recommended_action": recommended_action,
    }


def _number(value: Any, *, default: float | int | None) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if default is None:
        return None
    return float(default)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
