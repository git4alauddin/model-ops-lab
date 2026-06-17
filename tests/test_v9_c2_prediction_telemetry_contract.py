from pathlib import Path

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.schemas import PredictionRequest, PredictionResponse
from app.observability.prediction_telemetry import (
    PREDICTION_FAILURE_EVENT,
    PREDICTION_SUCCESS_EVENT,
    PREDICTION_TELEMETRY_VERSION,
    PREDICTION_VALIDATION_FAILURE_EVENT,
    build_prediction_failure_event,
    build_prediction_success_event,
    build_prediction_validation_failure_event,
    prediction_telemetry_fields,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = PROJECT_ROOT / "docs" / "monitoring" / "prediction_telemetry_contract.md"


def test_prediction_telemetry_contract_document_exists() -> None:
    contract = CONTRACT_PATH.read_text()

    required_terms = [
        "logs/predictions.jsonl",
        "prediction_success",
        "prediction_failure",
        "prediction_validation_failure",
        "DEPLOYMENT_VERSION",
        "FastAPI `422`",
    ]

    for term in required_terms:
        assert term in contract


def test_prediction_telemetry_fields_are_stable() -> None:
    assert prediction_telemetry_fields() == (
        "event_version",
        "event_type",
        "timestamp",
        "request_id",
        "endpoint",
        "status",
        "input_schema_version",
        "model_name",
        "model_version",
        "serving_environment",
        "deployment_version",
        "prediction",
        "probability",
        "latency_ms",
        "error_category",
        "error_message",
        "failure_stage",
    )


def test_success_event_contains_traceable_prediction_metadata() -> None:
    event = build_prediction_success_event(
        PredictionRequest(**_valid_prediction_payload()),
        PredictionResponse(
            prediction=1,
            probability=0.82,
            model_name="customer_churn_model",
            model_version="v1-test",
            request_id="request-1",
            latency_ms=4.2,
        ),
        endpoint="/predict",
        serving_environment="local",
        deployment_version="git-sha-1",
        timestamp="2026-06-17T00:00:00+00:00",
    )

    assert event["event_version"] == PREDICTION_TELEMETRY_VERSION
    assert event["event_type"] == PREDICTION_SUCCESS_EVENT
    assert event["input_schema_version"] == "v1"
    assert event["model_version"] == "v1-test"
    assert event["deployment_version"] == "git-sha-1"
    assert event["error_category"] is None


def test_failure_event_contains_error_category_and_stage() -> None:
    event = build_prediction_failure_event(
        PredictionRequest(**_valid_prediction_payload()),
        request_id="request-1",
        endpoint="/predict",
        error_category="model_loading",
        error_message="No champion model found.",
        failure_stage="model_loading",
        serving_environment="local",
        deployment_version="git-sha-1",
        timestamp="2026-06-17T00:00:00+00:00",
    )

    assert event["event_type"] == PREDICTION_FAILURE_EVENT
    assert event["status"] == "failed"
    assert event["model_version"] is None
    assert event["prediction"] is None
    assert event["error_category"] == "model_loading"
    assert event["failure_stage"] == "model_loading"


def test_validation_failure_event_is_separate_from_prediction_failure() -> None:
    event = build_prediction_validation_failure_event(
        request_id="request-1",
        endpoint="/predict",
        error_message="Request validation failed: 1 error.",
        serving_environment="local",
        deployment_version="git-sha-1",
        timestamp="2026-06-17T00:00:00+00:00",
    )

    assert event["event_type"] == PREDICTION_VALIDATION_FAILURE_EVENT
    assert event["error_category"] == "schema_validation"
    assert event["failure_stage"] == "validation"
    assert event["input_schema_version"] is None


def test_predict_validation_failure_logs_telemetry_without_changing_422(monkeypatch):
    records = []
    monkeypatch.setattr(
        "app.api.validation_handlers.write_prediction_log",
        lambda record, **kwargs: records.append(record),
    )
    client = TestClient(create_app())

    response = client.post(
        "/predict",
        json=_valid_prediction_payload(contract_type="monthly"),
    )

    assert response.status_code == 422
    assert len(records) == 1
    assert records[0]["event_type"] == PREDICTION_VALIDATION_FAILURE_EVENT
    assert records[0]["endpoint"] == "/predict"
    assert records[0]["error_category"] == "schema_validation"


def _valid_prediction_payload(**overrides):
    payload = {
        "schema_version": "v1",
        "tenure_months": 12,
        "monthly_charges": 79.5,
        "total_charges": 950.0,
        "contract_type": "month_to_month",
        "internet_service": "fiber_optic",
        "payment_method": "credit_card",
        "is_senior": False,
    }
    payload.update(overrides)
    return payload
