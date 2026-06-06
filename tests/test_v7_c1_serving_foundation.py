"""Serving API foundation checks for V7-C1."""

import warnings

warnings.filterwarnings(
    "ignore",
    message="Using `httpx` with `starlette.testclient` is deprecated.*",
    category=Warning,
)

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.constants import API_VERSION, SERVICE_NAME
from app.serve_api import app


def test_create_app_returns_fastapi_application():
    api_app = create_app()

    assert api_app.title == "ModelOpsLab Serving API"
    assert api_app.version == API_VERSION


def test_serve_api_exposes_importable_app():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200


def test_health_endpoint_returns_service_status():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.json() == {
        "status": "ok",
        "service": SERVICE_NAME,
        "api_version": API_VERSION,
    }
