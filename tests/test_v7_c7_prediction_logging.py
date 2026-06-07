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
        "timestamp": "2026-06-07T00:00:00+00:00",
        "request_id": "request-1",
        "status": "success",
        "model_name": "customer_churn_model",
        "model_version": "v1-test",
        "schema_version": "v1",
        "prediction": 1,
        "probability": 0.82,
        "latency_ms": 4.2,
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
        "timestamp": "2026-06-07T00:00:00+00:00",
        "request_id": "request-1",
        "status": "failed",
        "schema_version": "v1",
        "error": "No champion model found.",
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
    assert records[0]["status"] == "success"
    assert records[0]["model_version"] == "v1-test"
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
    assert records[0]["status"] == "failed"
    assert records[0]["error"] == "No champion model found."
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
    assert records[0]["status"] == "failed"
    assert records[0]["error"] == "Prediction failed."
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
