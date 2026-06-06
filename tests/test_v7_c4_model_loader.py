"""Registry-based model loader checks for V7-C4."""

from pathlib import Path

import joblib
import pytest

from app.model_registry import build_model_version_metadata, save_model_version_metadata
from app.serving.model_loader import (
    load_champion_model,
    ModelLoaderError,
    resolve_champion_model_metadata,
    resolve_model_artifact_path,
)


def test_resolve_champion_model_metadata_returns_single_champion(tmp_path):
    metadata = _save_registry_record(
        tmp_path,
        model_version="v1-loader",
        artifact_uri="artifacts/model.pkl",
    )

    champion = resolve_champion_model_metadata(registry_dir=tmp_path)

    assert champion["model_version"] == metadata["model_version"]
    assert champion["status"] == "champion"


def test_resolve_champion_model_metadata_rejects_missing_champion(tmp_path):
    with pytest.raises(ModelLoaderError, match="No champion model found"):
        resolve_champion_model_metadata(registry_dir=tmp_path)


def test_resolve_champion_model_metadata_rejects_multiple_champions(tmp_path):
    _save_registry_record(tmp_path, model_version="v1-first")
    _save_registry_record(tmp_path, model_version="v1-second", mlflow_run_id="run-2")

    with pytest.raises(ModelLoaderError, match="Multiple champion models found"):
        resolve_champion_model_metadata(registry_dir=tmp_path)


def test_resolve_model_artifact_path_accepts_local_file_path(tmp_path):
    model_path = tmp_path / "model.pkl"
    joblib.dump({"model": "local"}, model_path)

    resolved_path = resolve_model_artifact_path(str(model_path))

    assert resolved_path == model_path


def test_resolve_model_artifact_path_resolves_mlflow_run_uri_to_model_file(tmp_path):
    mlruns_dir = _save_mlflow_model_artifact(
        tmp_path,
        run_id="run-1",
        model={"model": "mlflow"},
    )

    resolved_path = resolve_model_artifact_path(
        "mlflow-run://run-1/artifacts/model",
        mlruns_dir=mlruns_dir,
    )

    assert resolved_path.name == "model.pkl"
    assert joblib.load(resolved_path) == {"model": "mlflow"}


def test_resolve_model_artifact_path_rejects_missing_artifact(tmp_path):
    with pytest.raises(ModelLoaderError, match="Model artifact not found"):
        resolve_model_artifact_path(str(tmp_path / "missing.pkl"))


def test_load_champion_model_loads_model_and_metadata(tmp_path):
    registry_dir = tmp_path / "registry"
    mlruns_dir = _save_mlflow_model_artifact(
        tmp_path,
        run_id="run-1",
        model={"model": "loaded"},
    )
    metadata = _save_registry_record(
        registry_dir,
        model_version="v1-loaded",
        artifact_uri="mlflow-run://run-1/artifacts/model",
    )

    loaded_model = load_champion_model(
        registry_dir=registry_dir,
        mlruns_dir=mlruns_dir,
    )

    assert loaded_model.model == {"model": "loaded"}
    assert loaded_model.metadata["model_version"] == metadata["model_version"]
    assert loaded_model.artifact_path.name == "model.pkl"


def test_load_champion_model_raises_when_artifact_cannot_be_loaded(tmp_path):
    registry_dir = tmp_path / "registry"
    artifact_path = tmp_path / "not-a-model.pkl"
    artifact_path.write_text("not a joblib artifact", encoding="utf-8")
    _save_registry_record(
        registry_dir,
        model_version="v1-bad-artifact",
        artifact_uri=str(artifact_path),
    )

    with pytest.raises(ModelLoaderError, match="Failed to load model artifact"):
        load_champion_model(registry_dir=registry_dir)


def _save_registry_record(
    output_dir: Path,
    *,
    model_version: str,
    mlflow_run_id: str = "run-1",
    artifact_uri: str = "mlflow-run://run-1/artifacts/model",
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
        artifact_uri=artifact_uri,
        promotion_reason="Test champion.",
    )
    save_model_version_metadata(metadata, output_dir=output_dir)
    return metadata


def _save_mlflow_model_artifact(
    tmp_path: Path,
    *,
    run_id: str,
    model: object,
) -> Path:
    artifact_dir = tmp_path / "mlruns" / "1" / run_id / "artifacts"
    artifact_dir.mkdir(parents=True)
    joblib.dump(model, artifact_dir / "model.pkl")
    return tmp_path / "mlruns"
