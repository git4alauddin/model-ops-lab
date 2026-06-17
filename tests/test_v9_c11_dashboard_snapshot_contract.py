import json
from pathlib import Path

import pytest

from app.observability.dashboard_snapshot import (
    DashboardSnapshotError,
    build_and_save_dashboard_snapshot,
    build_dashboard_snapshot,
    load_dashboard_source,
    save_dashboard_snapshot,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"


def test_dashboard_snapshot_combines_monitoring_and_drift_cards() -> None:
    snapshot = build_dashboard_snapshot(
        prediction_summary=_prediction_summary(),
        alerts=_alerts(),
        reference_baseline=_reference_baseline(),
        inference_snapshot=_inference_snapshot(),
        data_drift_summary=_data_drift_summary(),
        generated_at="2026-06-17T00:00:00+00:00",
    )

    assert snapshot["snapshot_version"] == "v1"
    assert snapshot["overall_status"] == "alerting"
    assert snapshot["cards"]["requests"]["request_count"] == 154
    assert snapshot["cards"]["alerts"]["active_alert_count"] == 3
    assert snapshot["cards"]["alerts"]["triggered_alert_names"] == [
        "high_failure_rate",
        "data_drift_detected",
    ]
    assert snapshot["cards"]["drift"]["overall_status"] == "drift_detected"
    assert snapshot["cards"]["drift"]["drifted_feature_count"] == 2
    assert snapshot["cards"]["telemetry_quality"]["feature_event_count"] == 16
    assert snapshot["distributions"]["drifted_features"] == [
        "contract_type",
        "tenure_months",
    ]


def test_dashboard_snapshot_records_report_freshness_and_sources() -> None:
    snapshot = build_dashboard_snapshot(
        prediction_summary=_prediction_summary(),
        alerts=_alerts(),
        reference_baseline=_reference_baseline(),
        inference_snapshot=_inference_snapshot(),
        data_drift_summary=_data_drift_summary(),
    )

    assert snapshot["report_freshness"] == {
        "prediction_summary_generated_at": "2026-06-17T00:01:00+00:00",
        "alerts_generated_at": "2026-06-17T00:02:00+00:00",
        "reference_baseline_generated_at": "2026-06-17T00:03:00+00:00",
        "inference_snapshot_generated_at": "2026-06-17T00:04:00+00:00",
        "data_drift_summary_generated_at": "2026-06-17T00:05:00+00:00",
    }
    assert snapshot["source_reports"]["prediction_summary"].endswith(
        "prediction_summary.json"
    )
    assert snapshot["source_reports"]["data_drift_summary"].endswith(
        "data_drift_summary.json"
    )


def test_load_dashboard_source_rejects_missing_or_invalid_file(tmp_path) -> None:
    with pytest.raises(DashboardSnapshotError, match="not found"):
        load_dashboard_source(tmp_path / "missing.json")

    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(DashboardSnapshotError, match="Invalid dashboard source JSON"):
        load_dashboard_source(invalid_path)


def test_save_and_build_dashboard_snapshot_persist_json(tmp_path) -> None:
    prediction_path = tmp_path / "prediction_summary.json"
    alerts_path = tmp_path / "alerts.json"
    reference_path = tmp_path / "reference_baseline.json"
    inference_path = tmp_path / "inference_snapshot.json"
    drift_path = tmp_path / "data_drift_summary.json"
    output_path = tmp_path / "dashboard_snapshot.json"

    prediction_path.write_text(json.dumps(_prediction_summary()), encoding="utf-8")
    alerts_path.write_text(json.dumps(_alerts()), encoding="utf-8")
    reference_path.write_text(json.dumps(_reference_baseline()), encoding="utf-8")
    inference_path.write_text(json.dumps(_inference_snapshot()), encoding="utf-8")
    drift_path.write_text(json.dumps(_data_drift_summary()), encoding="utf-8")

    snapshot = build_and_save_dashboard_snapshot(
        prediction_summary_path=prediction_path,
        alerts_path=alerts_path,
        reference_baseline_path=reference_path,
        inference_snapshot_path=inference_path,
        data_drift_summary_path=drift_path,
        output_path=output_path,
    )

    assert output_path.is_file()
    assert json.loads(output_path.read_text(encoding="utf-8")) == snapshot

    second_output = tmp_path / "copy.json"
    save_dashboard_snapshot(snapshot, second_output)

    assert json.loads(second_output.read_text(encoding="utf-8")) == snapshot


def test_v9_c11_docs_mention_dashboard_snapshot_command_and_report() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()

    assert "python -m app.build_dashboard_snapshot" in readme
    assert "reports/monitoring/dashboard_snapshot.json" in readme
    assert "V9-C11: Monitoring Dashboard Data Contract" in implementation


def _prediction_summary() -> dict:
    return {
        "generated_at": "2026-06-17T00:01:00+00:00",
        "request_count": 154,
        "success_count": 18,
        "failure_count": 136,
        "failure_rate": 0.883117,
        "raw_event_count": 325,
        "skipped_event_count": 171,
        "latency_ms": {"p95": 22.24},
        "prediction_distribution": {"0": 3, "1": 15},
        "probability_distribution": {"count": 18},
    }


def _alerts() -> dict:
    return {
        "generated_at": "2026-06-17T00:02:00+00:00",
        "overall_status": "alerting",
        "active_alert_count": 3,
        "alerts": [
            {"name": "missing_prediction_telemetry", "status": "ok"},
            {"name": "high_failure_rate", "status": "triggered"},
            {"name": "data_drift_detected", "status": "triggered"},
        ],
    }


def _reference_baseline() -> dict:
    return {
        "generated_at": "2026-06-17T00:03:00+00:00",
        "row_count": 20,
    }


def _inference_snapshot() -> dict:
    return {
        "generated_at": "2026-06-17T00:04:00+00:00",
        "feature_event_count": 16,
    }


def _data_drift_summary() -> dict:
    return {
        "generated_at": "2026-06-17T00:05:00+00:00",
        "overall_status": "drift_detected",
        "drifted_feature_count": 2,
        "insufficient_feature_count": 0,
        "reference_row_count": 20,
        "inference_row_count": 16,
        "features": {
            "tenure_months": {"status": "drift_detected"},
            "contract_type": {"status": "drift_detected"},
            "is_senior": {"status": "ok"},
        },
    }
