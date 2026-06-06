"""FastAPI application factory for the ModelOpsLab serving API."""

from fastapi import FastAPI

from app.api.constants import API_VERSION
from app.api.routes import router


def create_app() -> FastAPI:
    """Create the serving API application."""
    app = FastAPI(
        title="ModelOpsLab Serving API",
        version=API_VERSION,
    )
    app.include_router(router)
    return app
