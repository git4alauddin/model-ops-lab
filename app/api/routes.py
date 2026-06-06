"""HTTP routes for the ModelOpsLab serving API."""

from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.constants import API_VERSION, SERVICE_NAME
from app.api.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    PredictionRequest,
)
from app.serving.model_loader import load_champion_model, ModelLoaderError
from app.serving.prediction_logging import (
    build_prediction_failure_log,
    build_prediction_success_log,
    write_prediction_log,
)
from app.serving.predictor import predict_customer_churn, PredictionError
from app.serving.readiness import build_readiness_status

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return basic service availability."""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "api_version": API_VERSION,
    }


@router.get("/ready", response_model=None)
def readiness_check():
    """Return whether the service is ready to serve a champion model."""
    readiness = build_readiness_status()
    if readiness["status"] != "ready":
        return JSONResponse(status_code=503, content=readiness)
    return readiness


@router.post("/predict", response_model=None)
def predict(request: PredictionRequest):
    """Return a churn prediction from the active champion model."""
    request_id = str(uuid4())
    try:
        loaded_model = load_champion_model()
        prediction_response = predict_customer_churn(
            request,
            loaded_model,
            request_id=request_id,
        )
    except ModelLoaderError as exc:
        write_prediction_log(
            build_prediction_failure_log(
                request,
                request_id=request_id,
                error=str(exc),
            )
        )
        return _error_response(
            status_code=503,
            request_id=request_id,
            error=str(exc),
        )
    except PredictionError as exc:
        write_prediction_log(
            build_prediction_failure_log(
                request,
                request_id=request_id,
                error=str(exc),
            )
        )
        return _error_response(
            status_code=500,
            request_id=request_id,
            error=str(exc),
        )

    write_prediction_log(build_prediction_success_log(request, prediction_response))
    return prediction_response


@router.post("/predict/batch", response_model=None)
def predict_batch(request: BatchPredictionRequest):
    """Return churn predictions for multiple validated request instances."""
    batch_request_id = str(uuid4())
    try:
        loaded_model = load_champion_model()
    except ModelLoaderError as exc:
        return _error_response(
            status_code=503,
            request_id=batch_request_id,
            error=str(exc),
        )

    predictions = []
    try:
        for index, instance in enumerate(request.instances):
            prediction_response = predict_customer_churn(
                instance,
                loaded_model,
                request_id=f"{batch_request_id}-{index}",
            )
            write_prediction_log(
                build_prediction_success_log(instance, prediction_response)
            )
            predictions.append(prediction_response)
    except PredictionError as exc:
        return _error_response(
            status_code=500,
            request_id=batch_request_id,
            error=str(exc),
        )

    return BatchPredictionResponse(
        request_id=batch_request_id,
        predictions=predictions,
    )


def _error_response(
    *,
    status_code: int,
    request_id: str,
    error: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "failed",
            "error": error,
            "request_id": request_id,
        },
    )
