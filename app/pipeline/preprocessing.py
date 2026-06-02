"""Preprocessing helpers for V1."""

from sklearn.model_selection import train_test_split


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


def build_preprocessing_pipeline():
    """Return preprocessing pipeline object.

    Implementation is added in a later chunk.
    """
    raise NotImplementedError("Preprocessing pipeline is not implemented yet.")
