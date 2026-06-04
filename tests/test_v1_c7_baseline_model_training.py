"""Tests for V1 baseline model training."""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from app.pipeline.preprocessing import (
    build_preprocessing_pipeline,
    identify_feature_types,
)
from app.pipeline.trainer import (
    TrainingError,
    build_model,
    build_training_pipeline,
    train_model,
)


def test_build_model_logistic_regression():
    model = build_model(
        {
            "type": "logistic_regression",
            "params": {"max_iter": 200},
        }
    )

    assert isinstance(model, LogisticRegression)
    assert model.max_iter == 200


def test_build_model_decision_tree():
    model = build_model(
        {
            "type": "decision_tree",
            "params": {"max_depth": 4, "random_state": 42},
        }
    )

    assert isinstance(model, DecisionTreeClassifier)
    assert model.max_depth == 4
    assert model.random_state == 42


def test_build_model_random_forest():
    model = build_model(
        {
            "type": "random_forest",
            "params": {"n_estimators": 10, "random_state": 42},
        }
    )

    assert isinstance(model, RandomForestClassifier)
    assert model.n_estimators == 10
    assert model.random_state == 42


def test_build_model_unsupported_type():
    try:
        build_model({"type": "svm", "params": {}})
    except TrainingError as exc:
        assert "Unsupported model type" in str(exc)
    else:
        raise AssertionError("Expected TrainingError for unsupported model type.")


def test_build_training_pipeline():
    features = pd.DataFrame(
        {
            "age": [30, 45, 50, 60],
            "plan": ["basic", "premium", "basic", "premium"],
        }
    )
    numeric_features, categorical_features = identify_feature_types(features)
    preprocessing_pipeline = build_preprocessing_pipeline(
        numeric_features,
        categorical_features,
    )
    model = build_model({"type": "logistic_regression", "params": {"max_iter": 200}})

    training_pipeline = build_training_pipeline(preprocessing_pipeline, model)

    assert isinstance(training_pipeline, Pipeline)
    assert list(training_pipeline.named_steps) == ["preprocessor", "model"]


def test_train_model_success():
    features = pd.DataFrame(
        {
            "age": [30, 45, 50, 60, 35, 55],
            "plan": ["basic", "premium", "basic", "premium", "basic", "premium"],
        }
    )
    target = pd.Series([0, 1, 0, 1, 0, 1], name="churn")
    numeric_features, categorical_features = identify_feature_types(features)
    preprocessing_pipeline = build_preprocessing_pipeline(
        numeric_features,
        categorical_features,
    )
    model = build_model({"type": "logistic_regression", "params": {"max_iter": 200}})
    training_pipeline = build_training_pipeline(preprocessing_pipeline, model)

    fitted_pipeline, duration = train_model(training_pipeline, features, target)

    assert hasattr(fitted_pipeline.named_steps["model"], "classes_")
    assert duration >= 0


def test_train_model_failure_invalid_target():
    features = pd.DataFrame(
        {
            "age": [30, 45, 50],
            "plan": ["basic", "premium", "basic"],
        }
    )
    target = pd.Series([1, 1, 1], name="churn")
    numeric_features, categorical_features = identify_feature_types(features)
    preprocessing_pipeline = build_preprocessing_pipeline(
        numeric_features,
        categorical_features,
    )
    model = build_model({"type": "logistic_regression", "params": {"max_iter": 200}})
    training_pipeline = build_training_pipeline(preprocessing_pipeline, model)

    try:
        train_model(training_pipeline, features, target)
    except TrainingError as exc:
        assert "Model training failed" in str(exc)
    else:
        raise AssertionError("Expected TrainingError for single-class target.")
