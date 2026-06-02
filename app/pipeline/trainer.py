"""Model training helpers for V1."""

from time import perf_counter

from sklearn.exceptions import NotFittedError
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


class TrainingError(ValueError):
    """Raised when model construction or training fails."""


def build_model(model_config: dict):
    """Build the configured baseline model."""
    model_type = model_config.get("type")
    model_params = model_config.get("params", {})

    if model_type != "logistic_regression":
        raise TrainingError(f"Unsupported model type: {model_type}")

    try:
        return LogisticRegression(**model_params)
    except TypeError as exc:
        raise TrainingError("Invalid logistic_regression parameters.") from exc


def build_training_pipeline(preprocessing_pipeline, model) -> Pipeline:
    """Combine preprocessing and model into one sklearn pipeline."""
    return Pipeline(
        steps=[
            ("preprocessor", preprocessing_pipeline),
            ("model", model),
        ]
    )


def train_model(training_pipeline: Pipeline, x_train, y_train):
    """Fit the training pipeline and return duration metadata."""
    start_time = perf_counter()
    try:
        fitted_pipeline = training_pipeline.fit(x_train, y_train)
    except (ValueError, TypeError, NotFittedError) as exc:
        raise TrainingError("Model training failed.") from exc

    duration_seconds = perf_counter() - start_time
    return fitted_pipeline, duration_seconds
