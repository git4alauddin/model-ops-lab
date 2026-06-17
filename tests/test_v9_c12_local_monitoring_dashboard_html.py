import json
from pathlib import Path

import pytest

from app.observability.monitoring_dashboard import (
    MonitoringDashboardError,
    build_and_save_monitoring_dashboard,
    load_dashboard_snapshot,
    render_monitoring_dashboard,
    save_monitoring_dashboard,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "lessons.md"


def test_render_monitoring_dashboard_includes_core_cards_and_sections() -> None:
    html = render_monitoring_dashboard(_dashboard_snapshot())

    assert "<title>ModelOpsLab Monitoring Dashboard</title>" in html
    assert "Requests" in html
    assert "Latency" in html
    assert "Alerts" in html
    assert "Drift" in html
    assert "Telemetry Quality" in html
    assert "Prediction Distribution" in html
    assert "Probability Distribution" in html
    assert "Drifted Features" in html
    assert "Report Freshness" in html
    assert "high_failure_rate, data_drift_detected" in html


def test_render_monitoring_dashboard_escapes_snapshot_values() -> None:
    snapshot = _dashboard_snapshot()
    snapshot["distributions"]["drifted_features"] = ["<script>alert(1)</script>"]

    html = render_monitoring_dashboard(snapshot)

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_build_and_save_monitoring_dashboard_persists_html(tmp_path) -> None:
    snapshot_path = tmp_path / "dashboard_snapshot.json"
    output_path = tmp_path / "dashboard.html"
    snapshot_path.write_text(json.dumps(_dashboard_snapshot()), encoding="utf-8")

    html = build_and_save_monitoring_dashboard(
        snapshot_path=snapshot_path,
        output_path=output_path,
    )

    assert output_path.is_file()
    assert output_path.read_text(encoding="utf-8") == html
    assert "ModelOpsLab Monitoring Dashboard" in html

    second_output = tmp_path / "copy.html"
    save_monitoring_dashboard(html, second_output)

    assert second_output.read_text(encoding="utf-8") == html


def test_load_dashboard_snapshot_rejects_missing_invalid_or_wrong_shape(tmp_path) -> None:
    with pytest.raises(MonitoringDashboardError, match="not found"):
        load_dashboard_snapshot(tmp_path / "missing.json")

    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(MonitoringDashboardError, match="Invalid dashboard snapshot JSON"):
        load_dashboard_snapshot(invalid_path)

    wrong_shape_path = tmp_path / "wrong_shape.json"
    wrong_shape_path.write_text("[]", encoding="utf-8")

    with pytest.raises(MonitoringDashboardError, match="must be a JSON object"):
        load_dashboard_snapshot(wrong_shape_path)


def test_render_monitoring_dashboard_requires_cards() -> None:
    with pytest.raises(MonitoringDashboardError, match="missing cards"):
        render_monitoring_dashboard({"snapshot_version": "v1"})


def test_v9_c12_docs_mention_dashboard_command_and_report() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "python -m app.build_monitoring_dashboard" in readme
    assert "reports/monitoring/dashboard.html" in readme
    assert "V9-C12: Local Monitoring Dashboard HTML" in implementation
    assert "A dashboard should read from the dashboard snapshot" in lessons


def _dashboard_snapshot() -> dict:
    return {
        "snapshot_version": "v1",
        "generated_at": "2026-06-17T00:00:00+00:00",
        "overall_status": "alerting",
        "cards": {
            "requests": {
                "request_count": 154,
                "success_count": 18,
                "failure_count": 136,
                "failure_rate": 0.883117,
            },
            "latency": {
                "average": 6.176,
                "count": 18,
                "p95": 22.245,
                "p99": 22.245,
            },
            "alerts": {
                "overall_status": "alerting",
                "active_alert_count": 3,
                "triggered_alert_names": [
                    "high_failure_rate",
                    "data_drift_detected",
                ],
            },
            "drift": {
                "overall_status": "drift_detected",
                "drifted_feature_count": 2,
                "reference_row_count": 20,
                "inference_row_count": 16,
            },
            "telemetry_quality": {
                "raw_event_count": 325,
                "skipped_event_count": 171,
                "feature_event_count": 16,
            },
        },
        "distributions": {
            "prediction_distribution": {"0": 3, "1": 15},
            "probability_distribution": {
                "count": 18,
                "average": 0.713333,
                "min": 0,
                "max": 1,
                "buckets": {"0.0-0.2": 3, "0.8-1.0": 15},
            },
            "drifted_features": ["contract_type", "tenure_months"],
        },
        "report_freshness": {
            "prediction_summary_generated_at": "2026-06-17T00:01:00+00:00",
            "alerts_generated_at": "2026-06-17T00:02:00+00:00",
            "data_drift_summary_generated_at": "2026-06-17T00:03:00+00:00",
        },
    }
