"""Prediction service logic for the serving layer."""

from time import perf_counter
from typing import Any

import pandas as pd

from app.api.schemas import PredictionRequest, PredictionResponse
from app.serving.model_loader import LoadedModel

PREDICTION_FEATURE_COLUMNS: tuple[str, ...] = (
    "tenure_months",
    "monthly_charges",
    "total_charges",
    "contract_type",
    "internet_service",
    "payment_method",
    "is_senior",
)


class PredictionError(ValueError):
    """Raised when a prediction cannot be produced safely."""


def predict_customer_churn(
    request: PredictionRequest,
    loaded_model: LoadedModel,
    *,
    request_id: str,
) -> PredictionResponse:
    """Run one validated prediction request through a loaded champion model."""
    if not request_id:
        raise PredictionError("request_id is required.")

    started_at = perf_counter()
    model_input = build_model_input_frame(request)
    try:
        raw_prediction = loaded_model.model.predict(model_input)
        prediction = _extract_prediction(raw_prediction)
        probability = _predict_probability(
            loaded_model.model,
            model_input,
            prediction,
        )
    except PredictionError:
        raise
    except Exception as exc:
        raise PredictionError("Prediction failed.") from exc

    latency_ms = (perf_counter() - started_at) * 1000
    metadata = loaded_model.metadata
    return PredictionResponse(
        prediction=prediction,
        probability=probability,
        model_name=metadata["model_name"],
        model_version=metadata["model_version"],
        request_id=request_id,
        latency_ms=latency_ms,
    )


def build_model_input_frame(request: PredictionRequest) -> pd.DataFrame:
    """Convert a validated API request into the model's expected input row."""
    payload = request.model_dump(exclude={"schema_version"})
    return pd.DataFrame([{column: payload[column] for column in PREDICTION_FEATURE_COLUMNS}])


def _extract_prediction(raw_prediction: Any) -> int:
    try:
        prediction = raw_prediction[0]
    except (TypeError, KeyError, IndexError) as exc:
        raise PredictionError("Model prediction output is empty or invalid.") from exc

    if hasattr(prediction, "item"):
        prediction = prediction.item()
    if isinstance(prediction, bool) or prediction not in (0, 1):
        raise PredictionError("Model prediction must be 0 or 1.")
    return int(prediction)


def _predict_probability(model: Any, model_input: pd.DataFrame, prediction: int) -> float:
    if not hasattr(model, "predict_proba"):
        return float(prediction)

    raw_probabilities = model.predict_proba(model_input)
    try:
        probabilities = raw_probabilities[0]
        probability = probabilities[1] if len(probabilities) > 1 else probabilities[0]
    except (TypeError, KeyError, IndexError) as exc:
        raise PredictionError("Model probability output is empty or invalid.") from exc

    if hasattr(probability, "item"):
        probability = probability.item()
    if isinstance(probability, bool) or not isinstance(probability, int | float):
        raise PredictionError("Model probability must be numeric.")
    if probability < 0 or probability > 1:
        raise PredictionError("Model probability must be between 0 and 1.")
    return float(probability)
