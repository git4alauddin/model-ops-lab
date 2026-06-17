import json
from pathlib import Path

import pytest

from app.observability.monitoring_summary import (
    MonitoringSummaryError,
    build_and_save_prediction_monitoring_summary,
    build_prediction_monitoring_summary,
    load_prediction_telemetry,
    save_prediction_monitoring_summary,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_ROOT / "README.md"
IMPLEMENTATION_PATH = PROJECT_ROOT / "docs" / "versions" / "v9" / "implementation.md"


def test_load_prediction_telemetry_reads_jsonl_events(tmp_path) -> None:
    log_path = tmp_path / "predictions.jsonl"
    events = [_success_event("request-1", prediction=1), _failure_event("request-2")]
    log_path.write_text(
        "\n".join(json.dumps(event) for event in events),
        encoding="utf-8",
    )

    assert load_prediction_telemetry(log_path) == events


def test_load_prediction_telemetry_rejects_missing_or_invalid_files(tmp_path) -> None:
    with pytest.raises(MonitoringSummaryError, match="not found"):
        load_prediction_telemetry(tmp_path / "missing.jsonl")

    invalid_path = tmp_path / "invalid.jsonl"
    invalid_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(MonitoringSummaryError, match="Invalid JSON telemetry"):
        load_prediction_telemetry(invalid_path)


def test_prediction_monitoring_summary_calculates_operational_metrics() -> None:
    events = [
        _success_event("request-1", latency_ms=10.0, prediction=1, probability=0.91),
        _success_event("request-2", latency_ms=20.0, prediction=0, probability=0.35),
        _success_event("request-3", latency_ms=30.0, prediction=1, probability=0.72),
        _failure_event("request-4", error_category="model_loading"),
        _validation_failure_event("request-5"),
    ]

    summary = build_prediction_monitoring_summary(
        events,
        source_path=Path("logs/predictions.jsonl"),
        generated_at="2026-06-17T00:00:00+00:00",
    )

    assert summary["total_events"] == 5
    assert summary["raw_event_count"] == 5
    assert summary["skipped_event_count"] == 0
    assert summary["skipped_events"] == {}
    assert summary["request_count"] == 5
    assert summary["success_count"] == 3
    assert summary["failure_count"] == 2
    assert summary["failure_rate"] == 0.4
    assert summary["event_counts"] == {
        "prediction_failure": 1,
        "prediction_success": 3,
        "prediction_validation_failure": 1,
    }
    assert summary["failure_categories"] == {
        "model_loading": 1,
        "schema_validation": 1,
    }


def test_prediction_monitoring_summary_skips_legacy_non_v9_records() -> None:
    events = [
        _success_event("request-1", latency_ms=10.0, prediction=1, probability=0.91),
        {
            "timestamp": "2026-06-07T00:00:00+00:00",
            "request_id": "legacy-1",
            "status": "success",
            "model_version": "v1-test",
        },
        {
            "event_version": "v0",
            "event_type": "prediction_success",
            "request_id": "legacy-2",
        },
        {
            "event_version": "v1",
            "request_id": "legacy-3",
        },
        {
            "event_version": "v1",
            "event_type": "unknown_event",
            "request_id": "legacy-4",
        },
    ]

    summary = build_prediction_monitoring_summary(events)

    assert summary["raw_event_count"] == 5
    assert summary["total_events"] == 1
    assert summary["request_count"] == 1
    assert summary["success_count"] == 1
    assert summary["failure_count"] == 0
    assert summary["failure_rate"] == 0.0
    assert summary["skipped_event_count"] == 4
    assert summary["skipped_events"] == {
        "missing_event_type": 1,
        "missing_event_version": 1,
        "unsupported_event_type": 1,
        "unsupported_event_version": 1,
    }
    assert "None" not in summary["event_counts"]
    assert "None" not in summary["endpoints"]


def test_prediction_monitoring_summary_rejects_only_legacy_records() -> None:
    with pytest.raises(MonitoringSummaryError, match="No supported V9"):
        build_prediction_monitoring_summary(
            [
                {
                    "timestamp": "2026-06-07T00:00:00+00:00",
                    "request_id": "legacy-1",
                    "status": "success",
                }
            ]
        )


def test_prediction_monitoring_summary_calculates_latency_and_distributions() -> None:
    events = [
        _success_event("request-1", latency_ms=1.0, prediction=0, probability=0.05),
        _success_event("request-2", latency_ms=2.0, prediction=0, probability=0.25),
        _success_event("request-3", latency_ms=3.0, prediction=1, probability=0.45),
        _success_event("request-4", latency_ms=4.0, prediction=1, probability=0.65),
        _success_event("request-5", latency_ms=5.0, prediction=1, probability=1.0),
    ]

    summary = build_prediction_monitoring_summary(events)

    assert summary["latency_ms"] == {
        "count": 5,
        "average": 3.0,
        "p95": 5.0,
        "p99": 5.0,
        "min": 1.0,
        "max": 5.0,
    }
    assert summary["prediction_distribution"] == {"0": 2, "1": 3}
    assert summary["probability_distribution"]["count"] == 5
    assert summary["probability_distribution"]["average"] == 0.48
    assert summary["probability_distribution"]["buckets"] == {
        "0.0-0.2": 1,
        "0.2-0.4": 1,
        "0.4-0.6": 1,
        "0.6-0.8": 1,
        "0.8-1.0": 1,
    }


def test_save_prediction_monitoring_summary_writes_json_report(tmp_path) -> None:
    output_path = tmp_path / "reports" / "monitoring" / "prediction_summary.json"
    summary = build_prediction_monitoring_summary(
        [_success_event("request-1")],
        generated_at="2026-06-17T00:00:00+00:00",
    )

    save_prediction_monitoring_summary(summary, output_path)

    assert json.loads(output_path.read_text(encoding="utf-8")) == summary


def test_build_and_save_prediction_monitoring_summary_uses_default_report_shape(
    tmp_path,
) -> None:
    log_path = tmp_path / "predictions.jsonl"
    output_path = tmp_path / "reports" / "monitoring" / "prediction_summary.json"
    log_path.write_text(json.dumps(_success_event("request-1")), encoding="utf-8")

    summary = build_and_save_prediction_monitoring_summary(
        log_path=log_path,
        output_path=output_path,
    )

    assert output_path.is_file()
    assert summary["source_path"] == str(log_path)
    assert summary["success_count"] == 1


def test_v9_c3_documentation_mentions_command_and_report() -> None:
    readme = README_PATH.read_text()
    implementation = IMPLEMENTATION_PATH.read_text()

    assert "python -m app.build_prediction_monitoring_summary" in readme
    assert "reports/monitoring/prediction_summary.json" in readme
    assert "V9-C3: Local Monitoring Summary From Prediction Telemetry" in implementation


def _success_event(
    request_id: str,
    *,
    latency_ms: float = 4.2,
    prediction: int = 1,
    probability: float = 0.82,
) -> dict:
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
        "prediction": prediction,
        "probability": probability,
        "latency_ms": latency_ms,
        "error_category": None,
        "error_message": None,
        "failure_stage": None,
    }


def _failure_event(
    request_id: str,
    *,
    error_category: str = "prediction",
) -> dict:
    return {
        "event_version": "v1",
        "event_type": "prediction_failure",
        "timestamp": "2026-06-17T00:00:00+00:00",
        "request_id": request_id,
        "endpoint": "/predict",
        "status": "failed",
        "input_schema_version": "v1",
        "model_name": None,
        "model_version": None,
        "serving_environment": "local",
        "deployment_version": "local",
        "prediction": None,
        "probability": None,
        "latency_ms": None,
        "error_category": error_category,
        "error_message": "Prediction failed.",
        "failure_stage": error_category,
    }


def _validation_failure_event(request_id: str) -> dict:
    return {
        "event_version": "v1",
        "event_type": "prediction_validation_failure",
        "timestamp": "2026-06-17T00:00:00+00:00",
        "request_id": request_id,
        "endpoint": "/predict",
        "status": "failed",
        "input_schema_version": None,
        "model_name": None,
        "model_version": None,
        "serving_environment": "local",
        "deployment_version": "local",
        "prediction": None,
        "probability": None,
        "latency_ms": None,
        "error_category": "schema_validation",
        "error_message": "Request validation failed: 1 error.",
        "failure_stage": "validation",
    }
