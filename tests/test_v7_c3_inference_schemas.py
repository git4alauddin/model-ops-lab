"""Inference schema checks for V7-C3."""

import pytest
from pydantic import ValidationError

from app.api.schemas import (
    PredictionRequest,
    PredictionResponse,
    SCHEMA_VERSION,
    ServingErrorResponse,
)


def test_prediction_request_accepts_valid_payload():
    request = PredictionRequest(**_valid_prediction_payload())

    assert request.schema_version == SCHEMA_VERSION
    assert request.tenure_months == 12
    assert request.contract_type == "month_to_month"
    assert request.model_dump()["payment_method"] == "credit_card"


def test_prediction_request_rejects_missing_required_field():
    payload = _valid_prediction_payload()
    payload.pop("monthly_charges")

    with pytest.raises(ValidationError) as exc_info:
        PredictionRequest(**payload)

    assert "monthly_charges" in str(exc_info.value)


def test_prediction_request_rejects_invalid_categorical_value():
    payload = _valid_prediction_payload(contract_type="monthly")

    with pytest.raises(ValidationError) as exc_info:
        PredictionRequest(**payload)

    assert "contract_type" in str(exc_info.value)


def test_prediction_request_rejects_invalid_numeric_range():
    payload = _valid_prediction_payload(tenure_months=-1)

    with pytest.raises(ValidationError) as exc_info:
        PredictionRequest(**payload)

    assert "tenure_months" in str(exc_info.value)


def test_prediction_request_rejects_unexpected_fields():
    payload = _valid_prediction_payload(extra_feature="not_allowed")

    with pytest.raises(ValidationError) as exc_info:
        PredictionRequest(**payload)

    assert "extra_feature" in str(exc_info.value)


def test_prediction_response_contains_prediction_metadata():
    response = PredictionResponse(
        prediction=1,
        probability=0.82,
        model_name="customer_churn_model",
        model_version="v1-ready",
        request_id="request-1",
        latency_ms=12.4,
    )

    assert response.model_dump() == {
        "status": "success",
        "prediction": 1,
        "probability": 0.82,
        "model_name": "customer_churn_model",
        "model_version": "v1-ready",
        "request_id": "request-1",
        "latency_ms": 12.4,
    }


def test_prediction_response_rejects_invalid_probability():
    with pytest.raises(ValidationError) as exc_info:
        PredictionResponse(
            prediction=1,
            probability=1.2,
            model_name="customer_churn_model",
            model_version="v1-ready",
            request_id="request-1",
            latency_ms=12.4,
        )

    assert "probability" in str(exc_info.value)


def test_serving_error_response_is_structured():
    response = ServingErrorResponse(
        error="Model unavailable.",
        request_id="request-1",
    )

    assert response.model_dump() == {
        "status": "failed",
        "error": "Model unavailable.",
        "request_id": "request-1",
    }


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
