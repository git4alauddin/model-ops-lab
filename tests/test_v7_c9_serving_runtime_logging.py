"""Serving runtime logging checks for V7-C9."""

from pathlib import Path
import warnings

warnings.filterwarnings(
    "ignore",
    message="Using `httpx` with `starlette.testclient` is deprecated.*",
    category=Warning,
)

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.schemas import PredictionResponse
from app.serving.model_loader import LoadedModel, ModelLoaderError
from app.serving.runtime_logging import (
    log_prediction_completed,
    log_prediction_failed,
    log_prediction_received,
)


def test_serving_runtime_log_writes_human_readable_events(tmp_path):
    log_path = tmp_path / "modelopslab.log"

    log_prediction_received(
        endpoint="/predict",
        request_id="request-1",
        log_path=log_path,
    )
    log_prediction_completed(
        endpoint="/predict",
        request_id="request-1",
        model_name="customer_churn_model",
        model_version="v1-test",
        prediction_count=1,
        log_path=log_path,
    )
    log_prediction_failed(
        endpoint="/predict",
        request_id="request-2",
        stage="model_loading",
        error="No champion model found.",
        log_path=log_path,
    )

    log_text = log_path.read_text(encoding="utf-8")
    assert "Prediction request received." in log_text
    assert "Prediction request completed." in log_text
    assert "Prediction request failed." in log_text
    assert "request_id=request-1" in log_text
    assert "model_version=v1-test" in log_text


def test_predict_endpoint_emits_runtime_logs_on_success(monkeypatch):
    events = _capture_route_runtime_logs(monkeypatch)
    monkeypatch.setattr("app.api.routes.write_prediction_log", lambda record: None)
    monkeypatch.setattr("app.api.routes.load_champion_model", lambda: _loaded_model())
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
    assert [event["event"] for event in events] == ["received", "completed"]
    assert events[0]["endpoint"] == "/predict"
    assert events[1]["prediction_count"] == 1


def test_predict_endpoint_emits_runtime_logs_on_model_loader_failure(monkeypatch):
    events = _capture_route_runtime_logs(monkeypatch)
    monkeypatch.setattr("app.api.routes.write_prediction_log", lambda record: None)

    def fail_load():
        raise ModelLoaderError("No champion model found.")

    monkeypatch.setattr("app.api.routes.load_champion_model", fail_load)
    client = TestClient(create_app())

    response = client.post("/predict", json=_valid_prediction_payload())

    assert response.status_code == 503
    assert [event["event"] for event in events] == ["received", "failed"]
    assert events[1]["stage"] == "model_loading"


def test_batch_predict_endpoint_emits_runtime_logs_on_success(monkeypatch):
    events = _capture_route_runtime_logs(monkeypatch)
    monkeypatch.setattr("app.api.routes.write_prediction_log", lambda record: None)
    monkeypatch.setattr("app.api.routes.load_champion_model", lambda: _loaded_model())
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

    response = client.post(
        "/predict/batch",
        json={"instances": [_valid_prediction_payload(), _valid_prediction_payload()]},
    )

    assert response.status_code == 200
    assert [event["event"] for event in events] == ["received", "completed"]
    assert events[0]["endpoint"] == "/predict/batch"
    assert events[0]["instances"] == 2
    assert events[1]["prediction_count"] == 2


def _capture_route_runtime_logs(monkeypatch):
    events = []

    def received(**kwargs):
        events.append({"event": "received", **kwargs})

    def completed(**kwargs):
        events.append({"event": "completed", **kwargs})

    def failed(**kwargs):
        events.append({"event": "failed", **kwargs})

    monkeypatch.setattr("app.api.routes.log_prediction_received", received)
    monkeypatch.setattr("app.api.routes.log_prediction_completed", completed)
    monkeypatch.setattr("app.api.routes.log_prediction_failed", failed)
    return events


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
