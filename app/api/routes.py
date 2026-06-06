"""HTTP routes for the ModelOpsLab serving API."""

from fastapi import APIRouter

from app.api.constants import API_VERSION, SERVICE_NAME

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return basic service availability."""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "api_version": API_VERSION,
    }
