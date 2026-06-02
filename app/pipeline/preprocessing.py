"""Preprocessing helpers for V1."""

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_string_dtype,
)
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class PreprocessingError(ValueError):
    """Raised when preprocessing input validation fails."""


def split_features_target(dataframe, target_column: str):
    """Split a dataframe into features and target."""
    if target_column not in dataframe.columns:
        raise PreprocessingError(f"Target column '{target_column}' not found.")

    features = dataframe.drop(columns=[target_column])
    target = dataframe[target_column]

    if features.empty or len(features.columns) == 0:
        raise PreprocessingError("No feature columns available after target split.")

    return features, target


def split_train_test(features, target, test_size: float, random_state: int):
    """Create a reproducible train-test split."""
    if len(features) != len(target):
        raise PreprocessingError("Features and target must have the same row count.")

    if features.empty or target.empty:
        raise PreprocessingError("Features and target must not be empty.")

    if not 0 < float(test_size) < 1:
        raise PreprocessingError("test_size must be between 0 and 1.")

    return train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_state,
    )


def identify_feature_types(features):
    """Identify numeric and categorical feature columns."""
    if features.empty or len(features.columns) == 0:
        raise PreprocessingError("Feature dataframe must not be empty.")

    numeric_features = []
    categorical_features = []
    unsupported_features = []

    for column in features.columns:
        dtype = features[column].dtype
        if is_numeric_dtype(dtype) and not is_bool_dtype(dtype):
            numeric_features.append(column)
        elif (
            is_object_dtype(dtype)
            or is_string_dtype(dtype)
            or is_bool_dtype(dtype)
            or isinstance(dtype, pd.CategoricalDtype)
        ):
            categorical_features.append(column)
        else:
            unsupported_features.append(column)

    if unsupported_features:
        raise PreprocessingError(
            f"Unsupported feature columns detected: {unsupported_features}"
        )

    if not numeric_features and not categorical_features:
        raise PreprocessingError("No supported feature columns available.")

    return numeric_features, categorical_features


def build_preprocessing_pipeline(numeric_features, categorical_features):
    """Build a reusable preprocessing pipeline."""
    if not numeric_features and not categorical_features:
        raise PreprocessingError(
            "At least one numeric or categorical feature is required."
        )

    transformers = []

    if numeric_features:
        transformers.append(("numeric", StandardScaler(), numeric_features))

    if categorical_features:
        transformers.append(
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            )
        )

    return ColumnTransformer(transformers=transformers)
