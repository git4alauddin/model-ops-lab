import json
from pathlib import Path

import pytest

from app.observability.monitoring_alerts import (
    MonitoringAlertsError,
    build_and_save_monitoring_alerts,
    evaluate_prediction_monitoring_alerts,
    load_data_drift_summary,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "lessons.md"


def test_alert_report_includes_triggered_data_drift_alert() -> None:
    report = evaluate_prediction_monitoring_alerts(
        _prediction_summary(),
        drift_summary=_drift_summary(
            overall_status="drift_detected",
            inference_row_count=16,
            drifted_feature_count=5,
        ),
    )

    alerts = {alert["name"]: alert for alert in report["alerts"]}

    assert report["overall_status"] == "alerting"
    assert alerts["data_drift_detected"]["status"] == "triggered"
    assert alerts["data_drift_detected"]["metric_value"] == 5.0
    assert alerts["data_drift_insufficient_data"]["status"] == "ok"
    assert report["drift_summary_generated_at"] == "2026-06-17T00:00:00+00:00"


def test_alert_report_includes_insufficient_drift_data_alert() -> None:
    report = evaluate_prediction_monitoring_alerts(
        _prediction_summary(),
        drift_summary=_drift_summary(
            overall_status="insufficient_data",
            inference_row_count=0,
            drifted_feature_count=0,
        ),
    )

    alerts = {alert["name"]: alert for alert in report["alerts"]}

    assert report["overall_status"] == "alerting"
    assert alerts["data_drift_detected"]["status"] == "ok"
    assert alerts["data_drift_insufficient_data"]["status"] == "triggered"
    assert alerts["data_drift_insufficient_data"]["metric_value"] == 0.0


def test_build_monitoring_alerts_loads_optional_drift_summary(tmp_path) -> None:
    summary_path = tmp_path / "prediction_summary.json"
    drift_path = tmp_path / "data_drift_summary.json"
    output_path = tmp_path / "alerts.json"
    summary_path.write_text(json.dumps(_prediction_summary()), encoding="utf-8")
    drift_path.write_text(
        json.dumps(
            _drift_summary(
                overall_status="drift_detected",
                inference_row_count=16,
                drifted_feature_count=5,
            )
        ),
        encoding="utf-8",
    )

    report = build_and_save_monitoring_alerts(
        summary_path=summary_path,
        drift_summary_path=drift_path,
        output_path=output_path,
    )

    alert_names = {alert["name"] for alert in report["alerts"]}

    assert output_path.is_file()
    assert "data_drift_detected" in alert_names
    assert "data_drift_insufficient_data" in alert_names


def test_load_data_drift_summary_rejects_missing_or_invalid_file(tmp_path) -> None:
    with pytest.raises(MonitoringAlertsError, match="not found"):
        load_data_drift_summary(tmp_path / "missing.json")

    invalid_path = tmp_path / "data_drift_summary.json"
    invalid_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(MonitoringAlertsError, match="Invalid data drift summary JSON"):
        load_data_drift_summary(invalid_path)


def test_v9_c10_docs_record_drift_alert_integration() -> None:
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "V9-C10: Drift Alert Integration" in implementation
    assert "data_drift_detected" in implementation
    assert "Drift alerts connect ML-specific monitoring to the same operational alert report" in lessons


def _prediction_summary() -> dict:
    return {
        "generated_at": "2026-06-17T00:00:00+00:00",
        "source_path": "logs/predictions.jsonl",
        "request_count": 100,
        "failure_rate": 0.01,
        "latency_ms": {"p95": 100.0},
        "raw_event_count": 100,
        "skipped_event_count": 0,
        "prediction_distribution": {"0": 45, "1": 55},
    }


def _drift_summary(
    *,
    overall_status: str,
    inference_row_count: int,
    drifted_feature_count: int,
) -> dict:
    return {
        "generated_at": "2026-06-17T00:00:00+00:00",
        "overall_status": overall_status,
        "inference_row_count": inference_row_count,
        "drifted_feature_count": drifted_feature_count,
    }
