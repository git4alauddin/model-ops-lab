import json
from pathlib import Path

import pytest

from app.observability.monitoring_alerts import (
    MonitoringAlertsError,
    build_and_save_monitoring_alerts,
    evaluate_prediction_monitoring_alerts,
    load_prediction_monitoring_summary,
    save_monitoring_alerts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"


def test_alert_report_is_ok_for_healthy_summary() -> None:
    report = evaluate_prediction_monitoring_alerts(
        _summary(
            request_count=100,
            failure_rate=0.01,
            p95_latency=100.0,
            raw_event_count=100,
            skipped_event_count=0,
            prediction_distribution={"0": 45, "1": 55},
        ),
        generated_at="2026-06-17T00:00:00+00:00",
    )

    assert report["overall_status"] == "ok"
    assert report["active_alert_count"] == 0
    assert {alert["name"] for alert in report["alerts"]} == {
        "missing_prediction_telemetry",
        "high_failure_rate",
        "high_p95_latency",
        "high_skipped_event_ratio",
        "prediction_distribution_collapse",
    }
    assert all(alert["status"] == "ok" for alert in report["alerts"])


def test_alert_report_flags_unhealthy_summary() -> None:
    report = evaluate_prediction_monitoring_alerts(
        _summary(
            request_count=92,
            failure_rate=0.923913,
            p95_latency=1500.0,
            raw_event_count=263,
            skipped_event_count=171,
            prediction_distribution={"1": 7},
        ),
        generated_at="2026-06-17T00:00:00+00:00",
    )

    triggered_alerts = {
        alert["name"]: alert for alert in report["alerts"] if alert["status"] == "triggered"
    }

    assert report["overall_status"] == "alerting"
    assert report["active_alert_count"] == 4
    assert triggered_alerts["high_failure_rate"]["severity"] == "critical"
    assert triggered_alerts["high_p95_latency"]["severity"] == "warning"
    assert triggered_alerts["high_skipped_event_ratio"]["metric_value"] == 0.65019
    assert triggered_alerts["prediction_distribution_collapse"]["metric_value"] == 1.0


def test_alert_report_flags_missing_telemetry() -> None:
    report = evaluate_prediction_monitoring_alerts(
        _summary(
            request_count=0,
            failure_rate=0.0,
            p95_latency=None,
            raw_event_count=0,
            skipped_event_count=0,
            prediction_distribution={},
        )
    )

    triggered_alerts = [
        alert for alert in report["alerts"] if alert["status"] == "triggered"
    ]

    assert len(triggered_alerts) == 1
    assert triggered_alerts[0]["name"] == "missing_prediction_telemetry"
    assert triggered_alerts[0]["severity"] == "critical"


def test_alert_thresholds_can_be_overridden() -> None:
    report = evaluate_prediction_monitoring_alerts(
        _summary(
            request_count=10,
            failure_rate=0.15,
            p95_latency=100.0,
            raw_event_count=10,
            skipped_event_count=0,
            prediction_distribution={"0": 5, "1": 5},
        ),
        thresholds={"max_failure_rate": 0.1},
    )

    triggered = [alert["name"] for alert in report["alerts"] if alert["status"] == "triggered"]

    assert triggered == ["high_failure_rate"]


def test_load_prediction_monitoring_summary_rejects_missing_or_invalid_file(tmp_path):
    with pytest.raises(MonitoringAlertsError, match="not found"):
        load_prediction_monitoring_summary(tmp_path / "missing.json")

    invalid_path = tmp_path / "prediction_summary.json"
    invalid_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(MonitoringAlertsError, match="Invalid monitoring summary JSON"):
        load_prediction_monitoring_summary(invalid_path)


def test_save_and_build_monitoring_alerts_persist_report(tmp_path) -> None:
    summary_path = tmp_path / "prediction_summary.json"
    output_path = tmp_path / "alerts.json"
    summary_path.write_text(json.dumps(_summary()), encoding="utf-8")

    report = build_and_save_monitoring_alerts(
        summary_path=summary_path,
        output_path=output_path,
    )

    assert output_path.is_file()
    assert json.loads(output_path.read_text(encoding="utf-8")) == report

    second_output_path = tmp_path / "alerts_copy.json"
    save_monitoring_alerts(report, second_output_path)

    assert json.loads(second_output_path.read_text(encoding="utf-8")) == report


def test_v9_c5_documentation_mentions_alert_command_and_report() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()

    assert "python -m app.build_monitoring_alerts" in readme
    assert "reports/monitoring/alerts.json" in readme
    assert "V9-C5: Monitoring Alert Rules Foundation" in implementation


def _summary(
    *,
    request_count: int = 100,
    failure_rate: float = 0.01,
    p95_latency: float | None = 100.0,
    raw_event_count: int = 100,
    skipped_event_count: int = 0,
    prediction_distribution: dict[str, int] | None = None,
) -> dict:
    return {
        "generated_at": "2026-06-17T00:00:00+00:00",
        "source_path": "logs/predictions.jsonl",
        "raw_event_count": raw_event_count,
        "total_events": request_count,
        "request_count": request_count,
        "success_count": max(0, request_count - int(request_count * failure_rate)),
        "failure_count": int(request_count * failure_rate),
        "failure_rate": failure_rate,
        "latency_ms": {
            "count": request_count,
            "average": p95_latency,
            "p95": p95_latency,
            "p99": p95_latency,
            "min": p95_latency,
            "max": p95_latency,
        },
        "skipped_event_count": skipped_event_count,
        "skipped_events": {},
        "prediction_distribution": prediction_distribution or {"0": 50, "1": 50},
    }
