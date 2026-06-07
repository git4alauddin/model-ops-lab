from pathlib import Path

from app.api.app import create_app
from app.api.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    PredictionRequest,
    PredictionResponse,
    ServingErrorResponse,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v7_closure_serving_routes_exist() -> None:
    routes = {
        (route.path, method)
        for route in create_app().routes
        for method in getattr(route, "methods", set())
    }

    assert ("/health", "GET") in routes
    assert ("/ready", "GET") in routes
    assert ("/predict", "POST") in routes
    assert ("/predict/batch", "POST") in routes


def test_v7_closure_inference_schema_surface_exists() -> None:
    schema_classes = [
        PredictionRequest,
        PredictionResponse,
        BatchPredictionRequest,
        BatchPredictionResponse,
        ServingErrorResponse,
    ]

    for schema_class in schema_classes:
        assert callable(schema_class)
        assert schema_class.model_json_schema()


def test_v7_closure_serving_modules_exist() -> None:
    expected_paths = [
        "app/api/app.py",
        "app/api/routes.py",
        "app/api/schemas.py",
        "app/serve_api.py",
        "app/serving/readiness.py",
        "app/serving/model_loader.py",
        "app/serving/predictor.py",
        "app/serving/prediction_logging.py",
        "app/serving/runtime_logging.py",
    ]

    for relative_path in expected_paths:
        assert (PROJECT_ROOT / relative_path).is_file()


def test_v7_closure_docs_and_diagram_exist() -> None:
    expected_paths = [
        "docs/diagrams/v7_serving_flow.md",
        "docs/versions/v7/overview.md",
        "docs/versions/v7/implementation.md",
        "docs/versions/v7/verification.md",
        "docs/versions/v7/lessons.md",
        "docs/versions/v7/issues_faced.md",
        "docs/versions/v7/commit_log.md",
    ]

    for relative_path in expected_paths:
        assert (PROJECT_ROOT / relative_path).is_file()


def test_v7_closure_overview_marks_version_complete() -> None:
    overview = (PROJECT_ROOT / "docs/versions/v7/overview.md").read_text()

    assert "V7 is complete." in overview
    assert "V7-C11: serving version closure." in overview
