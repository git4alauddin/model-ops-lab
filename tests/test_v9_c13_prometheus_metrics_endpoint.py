import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.app import create_app
from app.observability.prometheus_metrics import (
    PrometheusMetricsError,
    build_prometheus_metrics_from_reports,
    load_prometheus_source,
    render_prometheus_metrics,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "lessons.md"


def test_prometheus_metrics_render_monitoring_and_drift_values() -> None:
    metrics = render_prometheus_metrics(
        prediction_summary=_prediction_summary(),
        alerts=_alerts(),
        data_drift_summary=_data_drift_summary(),
        generated_at="2026-06-17T00:00:00+00:00",
    ).decode("utf-8")

    assert 'modelopslab_monitoring_report_available{report="prediction_summary"} 1.0' in metrics
    assert "modelopslab_prediction_requests 154.0" in metrics
    assert "modelopslab_prediction_failure_rate 0.883117" in metrics
    assert 'modelopslab_prediction_latency_ms{stat="p95"} 22.245' in metrics
    assert "modelopslab_monitoring_active_alerts 3.0" in metrics
    assert "modelopslab_data_drift_detected 1.0" in metrics
    assert "modelopslab_data_drifted_features 5.0" in metrics


def test_prometheus_metrics_handles_missing_reports_as_unavailable() -> None:
    metrics = render_prometheus_metrics().decode("utf-8")

    assert 'modelopslab_monitoring_report_available{report="prediction_summary"} 0.0' in metrics
    assert 'modelopslab_monitoring_report_available{report="alerts"} 0.0' in metrics
    assert 'modelopslab_monitoring_report_available{report="data_drift_summary"} 0.0' in metrics
    assert "modelopslab_prediction_requests 0.0" in metrics


def test_build_prometheus_metrics_from_reports_loads_available_files(tmp_path) -> None:
    prediction_path = tmp_path / "prediction_summary.json"
    alerts_path = tmp_path / "alerts.json"
    drift_path = tmp_path / "data_drift_summary.json"
    prediction_path.write_text(json.dumps(_prediction_summary()), encoding="utf-8")
    alerts_path.write_text(json.dumps(_alerts()), encoding="utf-8")
    drift_path.write_text(json.dumps(_data_drift_summary()), encoding="utf-8")

    metrics = build_prometheus_metrics_from_reports(
        prediction_summary_path=prediction_path,
        alerts_path=alerts_path,
        data_drift_summary_path=drift_path,
    ).decode("utf-8")

    assert "modelopslab_prediction_successes 18.0" in metrics
    assert "modelopslab_data_drift_inference_rows 16.0" in metrics


def test_load_prometheus_source_rejects_missing_invalid_or_wrong_shape(tmp_path) -> None:
    with pytest.raises(PrometheusMetricsError, match="not found"):
        load_prometheus_source(tmp_path / "missing.json")

    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(PrometheusMetricsError, match="Invalid Prometheus source JSON"):
        load_prometheus_source(invalid_path)

    wrong_shape_path = tmp_path / "wrong_shape.json"
    wrong_shape_path.write_text("[]", encoding="utf-8")

    with pytest.raises(PrometheusMetricsError, match="must be a JSON object"):
        load_prometheus_source(wrong_shape_path)


def test_metrics_endpoint_returns_prometheus_text(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.routes.build_prometheus_metrics_from_reports",
        lambda: render_prometheus_metrics(
            prediction_summary=_prediction_summary(),
            alerts=_alerts(),
            data_drift_summary=_data_drift_summary(),
        ),
    )
    client = TestClient(create_app())

    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "modelopslab_prediction_requests 154.0" in response.text


def test_v9_c13_docs_mention_prometheus_metrics_endpoint() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "GET /metrics" in readme
    assert "prometheus-client" in readme
    assert "V9-C13: Prometheus Metrics Endpoint" in implementation
    assert "Prometheus gives Grafana a scrapeable metrics source" in lessons


def _prediction_summary() -> dict:
    return {
        "request_count": 154,
        "success_count": 18,
        "failure_count": 136,
        "failure_rate": 0.883117,
        "raw_event_count": 325,
        "skipped_event_count": 171,
        "latency_ms": {
            "average": 6.176,
            "p95": 22.245,
            "p99": 22.245,
            "min": 4.2,
            "max": 22.245,
        },
    }


def _alerts() -> dict:
    return {
        "overall_status": "alerting",
        "active_alert_count": 3,
    }


def _data_drift_summary() -> dict:
    return {
        "overall_status": "drift_detected",
        "drifted_feature_count": 5,
        "inference_row_count": 16,
    }
