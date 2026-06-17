import json
from pathlib import Path

import pytest

from app.observability.retraining_trigger import (
    INSUFFICIENT_MONITORING_DATA,
    RETRAINING_NOT_REQUIRED,
    RETRAINING_RECOMMENDED,
    RetrainingTriggerError,
    build_and_save_retraining_trigger_decision,
    evaluate_retraining_trigger,
    load_retraining_source,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v10" / "lessons.md"


def test_retraining_trigger_recommends_retraining_from_drift_and_failure_alerts() -> None:
    report = evaluate_retraining_trigger(
        alert_report=_alert_report(
            alerts=[
                _alert("high_failure_rate", status="triggered", severity="critical"),
                _alert("data_drift_detected", status="triggered"),
            ]
        ),
        drift_summary=_drift_summary(
            overall_status="drift_detected",
            inference_row_count=16,
            drifted_feature_count=5,
        ),
        generated_at="2026-06-17T00:00:00+00:00",
    )

    reason_names = {reason["name"] for reason in report["reasons"]}

    assert report["decision"] == RETRAINING_RECOMMENDED
    assert report["reason_count"] == 3
    assert "high_failure_rate" in reason_names
    assert "data_drift_detected" in reason_names
    assert report["source_freshness"]["alerts_generated_at"] == "2026-06-17T00:00:00+00:00"


def test_retraining_trigger_blocks_when_monitoring_data_is_insufficient() -> None:
    report = evaluate_retraining_trigger(
        alert_report=_alert_report(
            alerts=[
                _alert(
                    "missing_prediction_telemetry",
                    status="triggered",
                    severity="critical",
                )
            ]
        ),
        drift_summary=_drift_summary(
            overall_status="insufficient_data",
            inference_row_count=0,
            drifted_feature_count=0,
        ),
    )

    reason_categories = {reason["category"] for reason in report["reasons"]}

    assert report["decision"] == INSUFFICIENT_MONITORING_DATA
    assert reason_categories == {"insufficient_data"}


def test_retraining_trigger_skips_retraining_when_signals_are_ok() -> None:
    report = evaluate_retraining_trigger(
        alert_report=_alert_report(alerts=[_alert("high_failure_rate", status="ok")]),
        drift_summary=_drift_summary(
            overall_status="ok",
            inference_row_count=20,
            drifted_feature_count=0,
        ),
    )

    assert report["decision"] == RETRAINING_NOT_REQUIRED
    assert report["reason_count"] == 0


def test_build_and_save_retraining_trigger_decision_persists_json(tmp_path) -> None:
    alerts_path = tmp_path / "alerts.json"
    drift_path = tmp_path / "data_drift_summary.json"
    output_path = tmp_path / "retraining_trigger_decision.json"
    alerts_path.write_text(
        json.dumps(_alert_report(alerts=[_alert("data_drift_detected", status="triggered")])),
        encoding="utf-8",
    )
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

    report = build_and_save_retraining_trigger_decision(
        alerts_path=alerts_path,
        drift_summary_path=drift_path,
        output_path=output_path,
    )

    persisted = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path.is_file()
    assert persisted == report
    assert persisted["decision"] == RETRAINING_RECOMMENDED


def test_load_retraining_source_rejects_missing_or_invalid_file(tmp_path) -> None:
    with pytest.raises(RetrainingTriggerError, match="not found"):
        load_retraining_source(tmp_path / "missing.json")

    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(RetrainingTriggerError, match="Invalid retraining source JSON"):
        load_retraining_source(invalid_path)


def test_v10_c2_docs_mention_trigger_command_and_report() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "python -m app.evaluate_retraining_trigger" in readme
    assert "reports/retraining/retraining_trigger_decision.json" in readme
    assert "V10-C2: Local Retraining Trigger Decision" in implementation
    assert "Trigger decisions connect monitoring to retraining" in lessons


def _alert_report(*, alerts: list[dict]) -> dict:
    return {
        "generated_at": "2026-06-17T00:00:00+00:00",
        "overall_status": "alerting",
        "active_alert_count": sum(1 for alert in alerts if alert["status"] == "triggered"),
        "alerts": alerts,
    }


def _alert(
    name: str,
    *,
    status: str,
    severity: str = "warning",
) -> dict:
    return {
        "name": name,
        "status": status,
        "severity": severity,
        "metric_value": 1,
        "threshold": 0,
        "message": "test alert",
        "recommended_action": "test action",
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
