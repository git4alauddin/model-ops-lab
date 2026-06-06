"""Prediction service checks for V7-C5."""

from pathlib import Path

import pytest

from app.api.schemas import PredictionRequest
from app.serving.model_loader import LoadedModel
from app.serving.predictor import (
    build_model_input_frame,
    predict_customer_churn,
    PREDICTION_FEATURE_COLUMNS,
    PredictionError,
)


def test_build_model_input_frame_uses_exact_feature_columns():
    request = PredictionRequest(**_valid_prediction_payload())

    model_input = build_model_input_frame(request)

    assert tuple(model_input.columns) == PREDICTION_FEATURE_COLUMNS
    assert model_input.to_dict(orient="records") == [
        {
            "tenure_months": 12,
            "monthly_charges": 79.5,
            "total_charges": 950.0,
            "contract_type": "month_to_month",
            "internet_service": "fiber_optic",
            "payment_method": "credit_card",
            "is_senior": False,
        }
    ]


def test_predict_customer_churn_returns_prediction_response_with_probability():
    loaded_model = _loaded_model(model=FakeModel(prediction=1, probability=0.82))

    response = predict_customer_churn(
        PredictionRequest(**_valid_prediction_payload()),
        loaded_model,
        request_id="request-1",
    )

    assert response.status == "success"
    assert response.prediction == 1
    assert response.probability == 0.82
    assert response.model_name == "customer_churn_model"
    assert response.model_version == "v1-test"
    assert response.request_id == "request-1"
    assert response.latency_ms >= 0


def test_predict_customer_churn_uses_prediction_as_probability_without_proba():
    loaded_model = _loaded_model(model=FakeModelWithoutProbability(prediction=0))

    response = predict_customer_churn(
        PredictionRequest(**_valid_prediction_payload()),
        loaded_model,
        request_id="request-1",
    )

    assert response.prediction == 0
    assert response.probability == 0.0


def test_predict_customer_churn_rejects_invalid_prediction_output():
    loaded_model = _loaded_model(model=FakeModel(prediction=3, probability=0.82))

    with pytest.raises(PredictionError, match="Model prediction must be 0 or 1"):
        predict_customer_churn(
            PredictionRequest(**_valid_prediction_payload()),
            loaded_model,
            request_id="request-1",
        )


def test_predict_customer_churn_rejects_invalid_probability_output():
    loaded_model = _loaded_model(model=FakeModel(prediction=1, probability=1.2))

    with pytest.raises(PredictionError, match="Model probability must be between 0 and 1"):
        predict_customer_churn(
            PredictionRequest(**_valid_prediction_payload()),
            loaded_model,
            request_id="request-1",
        )


def test_predict_customer_churn_wraps_model_prediction_failure():
    loaded_model = _loaded_model(model=FailingModel())

    with pytest.raises(PredictionError, match="Prediction failed"):
        predict_customer_churn(
            PredictionRequest(**_valid_prediction_payload()),
            loaded_model,
            request_id="request-1",
        )


def test_predict_customer_churn_requires_request_id():
    loaded_model = _loaded_model(model=FakeModel(prediction=1, probability=0.82))

    with pytest.raises(PredictionError, match="request_id is required"):
        predict_customer_churn(
            PredictionRequest(**_valid_prediction_payload()),
            loaded_model,
            request_id="",
        )


class FakeModel:
    def __init__(self, *, prediction: int, probability: float) -> None:
        self.prediction = prediction
        self.probability = probability

    def predict(self, model_input):
        assert tuple(model_input.columns) == PREDICTION_FEATURE_COLUMNS
        return [self.prediction]

    def predict_proba(self, model_input):
        assert tuple(model_input.columns) == PREDICTION_FEATURE_COLUMNS
        return [[1 - self.probability, self.probability]]


class FakeModelWithoutProbability:
    def __init__(self, *, prediction: int) -> None:
        self.prediction = prediction

    def predict(self, model_input):
        assert tuple(model_input.columns) == PREDICTION_FEATURE_COLUMNS
        return [self.prediction]


class FailingModel:
    def predict(self, model_input):
        raise RuntimeError("model exploded")


def _loaded_model(model) -> LoadedModel:
    return LoadedModel(
        model=model,
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
