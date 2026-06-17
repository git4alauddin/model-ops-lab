"""Prediction logging checks for V7-C7."""

from pathlib import Path
import json
import warnings

warnings.filterwarnings(
    "ignore",
    message="Using `httpx` with `starlette.testclient` is deprecated.*",
    category=Warning,
)

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.schemas import PredictionRequest, PredictionResponse
from app.serving.model_loader import LoadedModel, ModelLoaderError
from app.serving.prediction_logging import (
    build_prediction_failure_log,
    build_prediction_success_log,
    write_prediction_log,
)
from app.serving.predictor import PredictionError


def test_write_prediction_log_appends_jsonl_record(tmp_path):
    log_path = tmp_path / "predictions.jsonl"
    record = {
        "timestamp": "2026-06-07T00:00:00+00:00",
        "request_id": "request-1",
        "status": "success",
    }

    write_prediction_log(record, log_path=log_path)

    assert json.loads(log_path.read_text(encoding="utf-8").strip()) == record


def test_success_log_record_contains_prediction_metadata():
    request = PredictionRequest(**_valid_prediction_payload())
    response = PredictionResponse(
        prediction=1,
        probability=0.82,
        model_name="customer_churn_model",
        model_version="v1-test",
        request_id="request-1",
        latency_ms=4.2,
    )

    record = build_prediction_success_log(
        request,
        response,
        timestamp="2026-06-07T00:00:00+00:00",
    )

    assert record == {
        "event_version": "v1",
        "event_type": "prediction_success",
        "timestamp": "2026-06-07T00:00:00+00:00",
        "request_id": "request-1",
        "endpoint": "/predict",
        "status": "success",
        "input_schema_version": "v1",
        "input_features": _expected_input_features(),
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


def test_failure_log_record_contains_error_metadata():
    request = PredictionRequest(**_valid_prediction_payload())

    record = build_prediction_failure_log(
        request,
        request_id="request-1",
        error="No champion model found.",
        timestamp="2026-06-07T00:00:00+00:00",
    )

    assert record == {
        "event_version": "v1",
        "event_type": "prediction_failure",
        "timestamp": "2026-06-07T00:00:00+00:00",
        "request_id": "request-1",
        "endpoint": "/predict",
        "status": "failed",
        "input_schema_version": "v1",
        "input_features": _expected_input_features(),
        "model_name": None,
        "model_version": None,
        "serving_environment": "local",
        "deployment_version": "local",
        "prediction": None,
        "probability": None,
        "latency_ms": None,
        "error_category": "prediction",
        "error_message": "No champion model found.",
        "failure_stage": "prediction",
    }


def test_predict_endpoint_logs_success(monkeypatch):
    records = []
    monkeypatch.setattr(
        "app.api.routes.write_prediction_log",
        lambda record, **kwargs: records.append(record),
    )
    monkeypatch.setattr(
        "app.api.routes.load_champion_model",
        lambda **kwargs: _loaded_model(),
    )
    monkeypatch.setattr(
        "app.api.routes.predict_customer_churn",
        lambda request, loaded_model, *, request_id: PredictionResponse(
            prediction=1,
            probability=0.82,
            model_name="customer_churn_model",
            model_version="v1-test",
            request_id=request_id,
            latency_ms=4.2,
        ),
    )
    client = TestClient(create_app())

    response = client.post("/predict", json=_valid_prediction_payload())

    assert response.status_code == 200
    assert len(records) == 1
    assert records[0]["event_version"] == "v1"
    assert records[0]["event_type"] == "prediction_success"
    assert records[0]["status"] == "success"
    assert records[0]["input_features"] == _expected_input_features()
    assert records[0]["model_version"] == "v1-test"
    assert records[0]["serving_environment"] == "local"
    assert records[0]["deployment_version"] == "local"
    assert records[0]["request_id"] == response.json()["request_id"]


def test_predict_endpoint_logs_model_loader_failure(monkeypatch):
    records = []

    def fail_load(**kwargs):
        raise ModelLoaderError("No champion model found.")

    monkeypatch.setattr(
        "app.api.routes.write_prediction_log",
        lambda record, **kwargs: records.append(record),
    )
    monkeypatch.setattr("app.api.routes.load_champion_model", fail_load)
    client = TestClient(create_app())

    response = client.post("/predict", json=_valid_prediction_payload())

    assert response.status_code == 503
    assert len(records) == 1
    assert records[0]["event_type"] == "prediction_failure"
    assert records[0]["status"] == "failed"
    assert records[0]["input_features"] == _expected_input_features()
    assert records[0]["error_category"] == "model_loading"
    assert records[0]["error_message"] == "No champion model found."
    assert records[0]["failure_stage"] == "model_loading"
    assert records[0]["request_id"] == response.json()["request_id"]


def test_predict_endpoint_logs_prediction_failure(monkeypatch):
    records = []

    def fail_predict(request, loaded_model, *, request_id: str):
        raise PredictionError("Prediction failed.")

    monkeypatch.setattr(
        "app.api.routes.write_prediction_log",
        lambda record, **kwargs: records.append(record),
    )
    monkeypatch.setattr(
        "app.api.routes.load_champion_model",
        lambda **kwargs: _loaded_model(),
    )
    monkeypatch.setattr("app.api.routes.predict_customer_churn", fail_predict)
    client = TestClient(create_app())

    response = client.post("/predict", json=_valid_prediction_payload())

    assert response.status_code == 500
    assert len(records) == 1
    assert records[0]["event_type"] == "prediction_failure"
    assert records[0]["status"] == "failed"
    assert records[0]["input_features"] == _expected_input_features()
    assert records[0]["error_category"] == "prediction"
    assert records[0]["error_message"] == "Prediction failed."
    assert records[0]["failure_stage"] == "prediction"
    assert records[0]["request_id"] == response.json()["request_id"]


def test_predict_endpoint_does_not_log_invalid_payload(monkeypatch):
    records = []
    monkeypatch.setattr(
        "app.api.routes.write_prediction_log",
        lambda record, **kwargs: records.append(record),
    )
    client = TestClient(create_app())

    response = client.post(
        "/predict",
        json=_valid_prediction_payload(contract_type="monthly"),
    )

    assert response.status_code == 422
    assert records == []


def _loaded_model() -> LoadedModel:
    return LoadedModel(
        model=object(),
        metadata={
            "model_name": "customer_churn_model",
            "model_version": "v1-test",
        },
        artifact_path=Path("model.pkl"),
    )


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


def _expected_input_features():
    payload = _valid_prediction_payload()
    payload.pop("schema_version")
    return payload
