"""Tests for V1 feature type detection."""

import pandas as pd

from app.pipeline.preprocessing import PreprocessingError, identify_feature_types


def test_identify_feature_types_mixed_columns():
    features = pd.DataFrame(
        {
            "age": [30, 45],
            "monthly_charges": [50.5, 89.9],
            "plan": ["basic", "premium"],
            "is_senior": [False, True],
        }
    )

    numeric_features, categorical_features = identify_feature_types(features)

    assert numeric_features == ["age", "monthly_charges"]
    assert categorical_features == ["plan", "is_senior"]


def test_identify_feature_types_numeric_only():
    features = pd.DataFrame({"age": [30, 45], "tenure": [12, 24]})

    numeric_features, categorical_features = identify_feature_types(features)

    assert numeric_features == ["age", "tenure"]
    assert categorical_features == []


def test_identify_feature_types_categorical_only():
    features = pd.DataFrame({"plan": ["basic", "premium"], "active": [True, False]})

    numeric_features, categorical_features = identify_feature_types(features)

    assert numeric_features == []
    assert categorical_features == ["plan", "active"]


def test_identify_feature_types_empty_dataframe():
    features = pd.DataFrame()

    try:
        identify_feature_types(features)
    except PreprocessingError as exc:
        assert "must not be empty" in str(exc)
    else:
        raise AssertionError("Expected PreprocessingError for empty features.")


def test_identify_feature_types_no_supported_columns():
    features = pd.DataFrame({"signup_date": pd.to_datetime(["2024-01-01", "2024-02-01"])})

    try:
        identify_feature_types(features)
    except PreprocessingError as exc:
        assert "Unsupported feature columns" in str(exc)
    else:
        raise AssertionError("Expected PreprocessingError for unsupported columns.")
