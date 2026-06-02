"""Tests for V1 preprocessing pipeline construction."""

import pandas as pd
from sklearn.compose import ColumnTransformer

from app.pipeline.preprocessing import (
    PreprocessingError,
    build_preprocessing_pipeline,
)


def test_build_preprocessing_pipeline_mixed_features():
    pipeline = build_preprocessing_pipeline(
        numeric_features=["age", "monthly_charges"],
        categorical_features=["plan"],
    )

    transformer_names = [name for name, _, _ in pipeline.transformers]

    assert isinstance(pipeline, ColumnTransformer)
    assert transformer_names == ["numeric", "categorical"]


def test_build_preprocessing_pipeline_numeric_only():
    pipeline = build_preprocessing_pipeline(
        numeric_features=["age", "monthly_charges"],
        categorical_features=[],
    )

    transformer_names = [name for name, _, _ in pipeline.transformers]

    assert transformer_names == ["numeric"]


def test_build_preprocessing_pipeline_categorical_only():
    pipeline = build_preprocessing_pipeline(
        numeric_features=[],
        categorical_features=["plan"],
    )

    transformer_names = [name for name, _, _ in pipeline.transformers]

    assert transformer_names == ["categorical"]


def test_build_preprocessing_pipeline_no_features():
    try:
        build_preprocessing_pipeline(numeric_features=[], categorical_features=[])
    except PreprocessingError as exc:
        assert "At least one" in str(exc)
    else:
        raise AssertionError("Expected PreprocessingError for no feature columns.")


def test_preprocessing_pipeline_handles_unknown_categories():
    train_features = pd.DataFrame(
        {
            "age": [30, 45, 50],
            "plan": ["basic", "premium", "basic"],
        }
    )
    test_features = pd.DataFrame(
        {
            "age": [40],
            "plan": ["enterprise"],
        }
    )
    pipeline = build_preprocessing_pipeline(
        numeric_features=["age"],
        categorical_features=["plan"],
    )

    pipeline.fit(train_features)
    transformed = pipeline.transform(test_features)

    assert transformed.shape[0] == 1
