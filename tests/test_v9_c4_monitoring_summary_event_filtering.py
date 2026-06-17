from pathlib import Path

import pytest

from app.observability.monitoring_summary import (
    MonitoringSummaryError,
    build_prediction_monitoring_summary,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"
LESSONS_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "lessons.md"


def test_monitoring_summary_filters_legacy_records_from_metrics() -> None:
    summary = build_prediction_monitoring_summary(
        [
            _valid_success_event("request-1"),
            {"request_id": "legacy-1", "status": "success"},
            {
                "event_version": "v1",
                "event_type": "unknown_event",
                "request_id": "legacy-2",
            },
        ]
    )

    assert summary["raw_event_count"] == 3
    assert summary["total_events"] == 1
    assert summary["request_count"] == 1
    assert summary["success_count"] == 1
    assert summary["failure_rate"] == 0.0
    assert summary["skipped_event_count"] == 2
    assert summary["skipped_events"] == {
        "missing_event_version": 1,
        "unsupported_event_type": 1,
    }


def test_monitoring_summary_fails_when_no_supported_v9_events_exist() -> None:
    with pytest.raises(MonitoringSummaryError, match="No supported V9"):
        build_prediction_monitoring_summary(
            [
                {"request_id": "legacy-1", "status": "success"},
                {"event_version": "v0", "request_id": "legacy-2"},
            ]
        )


def test_v9_c4_docs_record_event_filtering_boundary() -> None:
    implementation = IMPLEMENTATION_PATH.read_text()
    lessons = LESSONS_PATH.read_text()

    assert "V9-C4: Monitoring Summary Event Filtering" in implementation
    assert "skipped_event_count" in implementation
    assert "Legacy telemetry should not pollute current monitoring metrics" in lessons


def _valid_success_event(request_id: str) -> dict:
    return {
        "event_version": "v1",
        "event_type": "prediction_success",
        "timestamp": "2026-06-17T00:00:00+00:00",
        "request_id": request_id,
        "endpoint": "/predict",
        "status": "success",
        "input_schema_version": "v1",
        "model_name": "customer_churn_model",
        "model_version": "v1-test",
        "serving_environment": "local",
        "deployment_version": "local",
        "prediction": 1,
        "probability": 0.82,
        "latency_ms": 4.2,
        "error_category": None,
        "error_message": None,
        "failure_stage": None,
    }
