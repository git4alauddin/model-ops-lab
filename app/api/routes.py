"""HTTP routes for the ModelOpsLab serving API."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.constants import API_VERSION, SERVICE_NAME
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
