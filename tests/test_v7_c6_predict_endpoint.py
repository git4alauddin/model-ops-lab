"""Prediction endpoint checks for V7-C6."""

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
from app.serving.predictor import PredictionError


def test_predict_endpoint_returns_prediction_response(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.load_champion_model",
        lambda: _loaded_model(),
    )

    def fake_predict_customer_churn(request, loaded_model, *, request_id: str):
        assert request.tenure_months == 12
        assert loaded_model.metadata["model_version"] == "v1-test"
        return PredictionResponse(
            prediction=1,
            probability=0.82,
            model_name="customer_churn_model",
            model_version="v1-test",
            request_id=request_id,
            latency_ms=4.2,
        )

    monkeypatch.setattr(
        "app.api.routes.predict_customer_churn",
        fake_predict_customer_churn,
    )
    client = TestClient(create_app())

    response = client.post("/predict", json=_valid_prediction_payload())

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["prediction"] == 1
    assert response.json()["probability"] == 0.82
    assert response.json()["model_version"] == "v1-test"
    assert response.json()["request_id"]


def test_predict_endpoint_returns_422_for_invalid_payload():
    client = TestClient(create_app())
    payload = _valid_prediction_payload(contract_type="monthly")

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_endpoint_returns_503_when_model_cannot_load(monkeypatch):
    def fail_load():
        raise ModelLoaderError("No champion model found.")

    monkeypatch.setattr("app.api.routes.load_champion_model", fail_load)
    client = TestClient(create_app())

    response = client.post("/predict", json=_valid_prediction_payload())

    assert response.status_code == 503
    assert response.json()["status"] == "failed"
    assert response.json()["error"] == "No champion model found."
    assert response.json()["request_id"]


def test_predict_endpoint_returns_500_when_prediction_fails(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.load_champion_model",
        lambda: _loaded_model(),
    )

    def fail_predict(request, loaded_model, *, request_id: str):
        raise PredictionError("Prediction failed.")

    monkeypatch.setattr("app.api.routes.predict_customer_churn", fail_predict)
    client = TestClient(create_app())

    response = client.post("/predict", json=_valid_prediction_payload())

    assert response.status_code == 500
    assert response.json()["status"] == "failed"
    assert response.json()["error"] == "Prediction failed."
    assert response.json()["request_id"]


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
