"""FastAPI application factory for the ModelOpsLab serving API."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.constants import API_VERSION
from app.api.routes import router
from app.api.validation_handlers import validation_exception_handler


def create_app() -> FastAPI:
    """Create the serving API application."""
    app = FastAPI(
        title="ModelOpsLab Serving API",
        version=API_VERSION,
    )
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    app.include_router(router)
    return app
