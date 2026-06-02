"""Tests for V1 artifact persistence."""

import json

import joblib
import pandas as pd

from app.pipeline.preprocessing import (
    build_preprocessing_pipeline,
    identify_feature_types,
)
from app.pipeline.trainer import build_model, build_training_pipeline, train_model
from app.utils.artifacts import (
    ArtifactError,
    build_artifact_paths,
    save_json,
    save_model,
)


def _fit_small_pipeline():
    features = pd.DataFrame(
        {
            "tenure_months": [2, 24, 5, 36, 1, 48],
            "monthly_charges": [70.3, 45.1, 89.9, 55.2, 95.0, 40.0],
            "contract_type": [
                "month_to_month",
                "one_year",
                "month_to_month",
                "two_year",
                "month_to_month",
                "two_year",
            ],
        }
    )
    target = pd.Series([1, 0, 1, 0, 1, 0], name="churn")
    numeric_features, categorical_features = identify_feature_types(features)
    preprocessing_pipeline = build_preprocessing_pipeline(
        numeric_features,
        categorical_features,
    )
    model = build_model({"type": "logistic_regression", "params": {"max_iter": 200}})
    training_pipeline = build_training_pipeline(preprocessing_pipeline, model)
    fitted_pipeline, _ = train_model(training_pipeline, features, target)
    return fitted_pipeline, features


def test_save_json_creates_file(tmp_path):
    output_path = tmp_path / "metrics.json"
    data = {"accuracy": 1.0, "confusion_matrix": [[1, 0], [0, 1]]}

    save_json(data, output_path)

    assert output_path.exists()
    assert json.loads(output_path.read_text(encoding="utf-8")) == data


def test_save_model_creates_loadable_artifact(tmp_path):
    fitted_pipeline, features = _fit_small_pipeline()
    output_path = tmp_path / "model.pkl"

    save_model(fitted_pipeline, output_path)
    loaded_pipeline = joblib.load(output_path)

    assert output_path.exists()
    assert len(loaded_pipeline.predict(features.head(1))) == 1


def test_build_artifact_paths_from_config():
    config = {
        "artifacts": {
            "dir": "artifacts",
            "model_file": "model.pkl",
            "metrics_file": "metrics.json",
            "config_snapshot_file": "config_snapshot.json",
            "metadata_file": "training_metadata.json",
        }
    }

    paths = build_artifact_paths(config)

    assert str(paths["model"]) == "artifacts\\model.pkl"
    assert str(paths["metrics"]) == "artifacts\\metrics.json"
    assert str(paths["config_snapshot"]) == "artifacts\\config_snapshot.json"
    assert str(paths["metadata"]) == "artifacts\\training_metadata.json"


def test_save_json_invalid_path_raises_artifact_error(tmp_path):
    invalid_path = tmp_path

    try:
        save_json({"accuracy": 1.0}, invalid_path)
    except ArtifactError as exc:
        assert "Failed to save JSON artifact" in str(exc)
    else:
        raise AssertionError("Expected ArtifactError for invalid JSON path.")
