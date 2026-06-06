"""Readiness endpoint checks for V7-C2."""

import warnings

warnings.filterwarnings(
    "ignore",
    message="Using `httpx` with `starlette.testclient` is deprecated.*",
    category=Warning,
)

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.model_registry import build_model_version_metadata, save_model_version_metadata
from app.serving.readiness import build_readiness_status


def test_readiness_status_is_ready_when_one_champion_exists(tmp_path):
    metadata = _save_registry_record(tmp_path, model_version="v1-ready")

    readiness = build_readiness_status(registry_dir=tmp_path)

    assert readiness == {
        "status": "ready",
        "service": "modelopslab-serving",
        "model_loaded": True,
        "model_name": metadata["model_name"],
        "model_version": metadata["model_version"],
        "mlflow_run_id": metadata["mlflow_run_id"],
    }


def test_readiness_status_is_not_ready_without_champion(tmp_path):
    readiness = build_readiness_status(registry_dir=tmp_path)

    assert readiness == {
        "status": "not_ready",
        "service": "modelopslab-serving",
        "model_loaded": False,
        "reason": "No champion model found.",
    }


def test_readiness_status_rejects_multiple_champions(tmp_path):
    _save_registry_record(tmp_path, model_version="v1-first")
    _save_registry_record(tmp_path, model_version="v1-second", mlflow_run_id="run-2")

    readiness = build_readiness_status(registry_dir=tmp_path)

    assert readiness == {
        "status": "not_ready",
        "service": "modelopslab-serving",
        "model_loaded": False,
        "reason": "Multiple champion models found.",
    }


def test_ready_endpoint_returns_ready_response(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.build_readiness_status",
        lambda: {
            "status": "ready",
            "service": "modelopslab-serving",
            "model_loaded": True,
            "model_name": "customer_churn_model",
            "model_version": "v1-ready",
            "mlflow_run_id": "run-1",
        },
    )
    client = TestClient(create_app())

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["model_version"] == "v1-ready"


def test_ready_endpoint_returns_503_when_not_ready(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.build_readiness_status",
        lambda: {
            "status": "not_ready",
            "service": "modelopslab-serving",
            "model_loaded": False,
            "reason": "No champion model found.",
        },
    )
    client = TestClient(create_app())

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "service": "modelopslab-serving",
        "model_loaded": False,
        "reason": "No champion model found.",
    }


def test_health_endpoint_remains_independent_from_readiness(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.build_readiness_status",
        lambda: {
            "status": "not_ready",
            "service": "modelopslab-serving",
            "model_loaded": False,
            "reason": "No champion model found.",
        },
    )
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def _save_registry_record(
    output_dir,
    *,
    model_version: str,
    mlflow_run_id: str = "run-1",
) -> dict:
    metadata = build_model_version_metadata(
        model_name="customer_churn_model",
        model_version=model_version,
        status="champion",
        mlflow_run_id=mlflow_run_id,
        candidate_name="logistic_regression",
        model_type="LogisticRegression",
        dataset_name="customer_churn",
        dataset_version="v1",
        dataset_checksum="abc123",
        metrics={"f1": 0.82},
        artifact_uri=f"mlflow-run://{mlflow_run_id}/artifacts/model",
        promotion_reason="Test champion.",
    )
    save_model_version_metadata(metadata, output_dir=output_dir)
    return metadata
