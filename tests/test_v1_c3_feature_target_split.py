"""Tests for V1 feature-target split behavior."""

import pandas as pd

from app.pipeline.preprocessing import PreprocessingError, split_features_target


def test_split_features_target_success():
    dataframe = pd.DataFrame(
        {
            "age": [30, 45],
            "plan": ["basic", "premium"],
            "churn": [0, 1],
        }
    )

    features, target = split_features_target(dataframe, "churn")

    assert "churn" not in features.columns
    assert list(features.columns) == ["age", "plan"]
    assert target.name == "churn"
    assert list(target) == [0, 1]


def test_split_features_target_missing_target():
    dataframe = pd.DataFrame({"age": [30, 45], "plan": ["basic", "premium"]})

    try:
        split_features_target(dataframe, "churn")
    except PreprocessingError as exc:
        assert "Target column" in str(exc)
    else:
        raise AssertionError("Expected PreprocessingError for missing target column.")


def test_split_features_target_no_feature_columns():
    dataframe = pd.DataFrame({"churn": [0, 1]})

    try:
        split_features_target(dataframe, "churn")
    except PreprocessingError as exc:
        assert "No feature columns" in str(exc)
    else:
        raise AssertionError("Expected PreprocessingError when no features remain.")
