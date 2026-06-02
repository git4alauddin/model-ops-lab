"""Tests for V1 evaluation metrics."""

import pandas as pd

from app.evaluate import EvaluationError, evaluate_model
from app.pipeline.preprocessing import (
    build_preprocessing_pipeline,
    identify_feature_types,
    split_train_test,
)
from app.pipeline.trainer import (
    build_model,
    build_training_pipeline,
    train_model,
)


def _train_small_pipeline():
    features = pd.DataFrame(
        {
            "tenure_months": [2, 24, 5, 36, 1, 48, 7, 30],
            "monthly_charges": [70.3, 45.1, 89.9, 55.2, 95.0, 40.0, 84.6, 50.7],
            "contract_type": [
                "month_to_month",
                "one_year",
                "month_to_month",
                "two_year",
                "month_to_month",
                "two_year",
                "month_to_month",
                "one_year",
            ],
        }
    )
    target = pd.Series([1, 0, 1, 0, 1, 0, 1, 0], name="churn")
    x_train, x_test, y_train, y_test = split_train_test(
        features,
        target,
        test_size=0.25,
        random_state=42,
    )
    numeric_features, categorical_features = identify_feature_types(x_train)
    preprocessing_pipeline = build_preprocessing_pipeline(
        numeric_features,
        categorical_features,
    )
    model = build_model({"type": "logistic_regression", "params": {"max_iter": 200}})
    training_pipeline = build_training_pipeline(preprocessing_pipeline, model)
    fitted_pipeline, _ = train_model(training_pipeline, x_train, y_train)
    return fitted_pipeline, x_test, y_test


def test_evaluate_model_returns_expected_metric_keys():
    fitted_pipeline, x_test, y_test = _train_small_pipeline()

    metrics = evaluate_model(fitted_pipeline, x_test, y_test)

    assert set(metrics) == {
        "accuracy",
        "precision",
        "recall",
        "f1",
        "confusion_matrix",
    }


def test_evaluate_model_metrics_are_numeric():
    fitted_pipeline, x_test, y_test = _train_small_pipeline()

    metrics = evaluate_model(fitted_pipeline, x_test, y_test)

    assert isinstance(metrics["accuracy"], float)
    assert isinstance(metrics["precision"], float)
    assert isinstance(metrics["recall"], float)
    assert isinstance(metrics["f1"], float)


def test_evaluate_model_confusion_matrix_shape():
    fitted_pipeline, x_test, y_test = _train_small_pipeline()

    metrics = evaluate_model(fitted_pipeline, x_test, y_test)

    assert len(metrics["confusion_matrix"]) == 2
    assert len(metrics["confusion_matrix"][0]) == 2


def test_evaluate_model_mismatched_lengths():
    fitted_pipeline, x_test, y_test = _train_small_pipeline()

    try:
        evaluate_model(fitted_pipeline, x_test, y_test.iloc[:-1])
    except EvaluationError as exc:
        assert "same row count" in str(exc)
    else:
        raise AssertionError("Expected EvaluationError for mismatched lengths.")


def test_evaluate_model_missing_predict():
    _, x_test, y_test = _train_small_pipeline()

    try:
        evaluate_model(object(), x_test, y_test)
    except EvaluationError as exc:
        assert "predict" in str(exc)
    else:
        raise AssertionError("Expected EvaluationError for missing predict method.")
