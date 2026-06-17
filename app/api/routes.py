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
from app.serving.runtime_logging import (
    log_prediction_completed,
    log_prediction_failed,
    log_prediction_received,
)
from app.serving.settings import get_serving_settings

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
    settings = get_serving_settings()
    readiness = build_readiness_status(registry_dir=settings.model_registry_dir)
    if readiness["status"] != "ready":
        return JSONResponse(status_code=503, content=readiness)
    return readiness


@router.post("/predict", response_model=None)
def predict(request: PredictionRequest):
    """Return a churn prediction from the active champion model."""
    settings = get_serving_settings()
    request_id = str(uuid4())
    log_prediction_received(
        endpoint="/predict",
        request_id=request_id,
        log_path=settings.app_log_path,
    )
    try:
        loaded_model = load_champion_model(
            registry_dir=settings.model_registry_dir,
            mlruns_dir=settings.mlflow_runs_dir,
        )
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
                endpoint="/predict",
                error_category="model_loading",
                failure_stage="model_loading",
                serving_environment=settings.modelopslab_env,
                deployment_version=settings.deployment_version,
            ),
            log_path=settings.prediction_log_path,
        )
        log_prediction_failed(
            endpoint="/predict",
            request_id=request_id,
            stage="model_loading",
            error=exc,
            log_path=settings.app_log_path,
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
                endpoint="/predict",
                error_category="prediction",
                failure_stage="prediction",
                serving_environment=settings.modelopslab_env,
                deployment_version=settings.deployment_version,
            ),
            log_path=settings.prediction_log_path,
        )
        log_prediction_failed(
            endpoint="/predict",
            request_id=request_id,
            stage="prediction",
            error=exc,
            log_path=settings.app_log_path,
        )
        return _error_response(
            status_code=500,
            request_id=request_id,
            error=str(exc),
        )

    write_prediction_log(
        build_prediction_success_log(
            request,
            prediction_response,
            endpoint="/predict",
            serving_environment=settings.modelopslab_env,
            deployment_version=settings.deployment_version,
        ),
        log_path=settings.prediction_log_path,
    )
    log_prediction_completed(
        endpoint="/predict",
        request_id=request_id,
        model_name=prediction_response.model_name,
        model_version=prediction_response.model_version,
        prediction_count=1,
        log_path=settings.app_log_path,
    )
    return prediction_response


@router.post("/predict/batch", response_model=None)
def predict_batch(request: BatchPredictionRequest):
    """Return churn predictions for multiple validated request instances."""
    settings = get_serving_settings()
    batch_request_id = str(uuid4())
    log_prediction_received(
        endpoint="/predict/batch",
        request_id=batch_request_id,
        instances=len(request.instances),
        log_path=settings.app_log_path,
    )
    try:
        loaded_model = load_champion_model(
            registry_dir=settings.model_registry_dir,
            mlruns_dir=settings.mlflow_runs_dir,
        )
    except ModelLoaderError as exc:
        write_prediction_log(
            build_prediction_failure_log(
                request.instances[0],
                request_id=batch_request_id,
                error=str(exc),
                endpoint="/predict/batch",
                error_category="model_loading",
                failure_stage="model_loading",
                serving_environment=settings.modelopslab_env,
                deployment_version=settings.deployment_version,
            ),
            log_path=settings.prediction_log_path,
        )
        log_prediction_failed(
            endpoint="/predict/batch",
            request_id=batch_request_id,
            stage="model_loading",
            error=exc,
            log_path=settings.app_log_path,
        )
        return _error_response(
            status_code=503,
            request_id=batch_request_id,
            error=str(exc),
        )

    predictions = []
    current_instance = request.instances[0]
    try:
        for index, instance in enumerate(request.instances):
            current_instance = instance
            prediction_response = predict_customer_churn(
                instance,
                loaded_model,
                request_id=f"{batch_request_id}-{index}",
            )
            write_prediction_log(
                build_prediction_success_log(
                    instance,
                    prediction_response,
                    endpoint="/predict/batch",
                    serving_environment=settings.modelopslab_env,
                    deployment_version=settings.deployment_version,
                ),
                log_path=settings.prediction_log_path,
            )
            predictions.append(prediction_response)
    except PredictionError as exc:
        write_prediction_log(
            build_prediction_failure_log(
                current_instance,
                request_id=batch_request_id,
                error=str(exc),
                endpoint="/predict/batch",
                error_category="prediction",
                failure_stage="prediction",
                serving_environment=settings.modelopslab_env,
                deployment_version=settings.deployment_version,
            ),
            log_path=settings.prediction_log_path,
        )
        log_prediction_failed(
            endpoint="/predict/batch",
            request_id=batch_request_id,
            stage="prediction",
            error=exc,
            log_path=settings.app_log_path,
        )
        return _error_response(
            status_code=500,
            request_id=batch_request_id,
            error=str(exc),
        )

    first_prediction = predictions[0]
    log_prediction_completed(
        endpoint="/predict/batch",
        request_id=batch_request_id,
        model_name=first_prediction.model_name,
        model_version=first_prediction.model_version,
        prediction_count=len(predictions),
        log_path=settings.app_log_path,
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
