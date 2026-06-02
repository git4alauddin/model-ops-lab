"""Evaluation helpers for V1."""

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


class EvaluationError(ValueError):
    """Raised when model evaluation fails."""


def evaluate_model(fitted_pipeline, x_test, y_test) -> dict:
    """Evaluate a fitted classification pipeline."""
    if not hasattr(fitted_pipeline, "predict"):
        raise EvaluationError("Fitted pipeline must expose a predict method.")

    if len(x_test) != len(y_test):
        raise EvaluationError("x_test and y_test must have the same row count.")

    try:
        y_pred = fitted_pipeline.predict(x_test)
    except (ValueError, TypeError) as exc:
        raise EvaluationError("Model prediction failed during evaluation.") from exc

    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=[0, 1]).tolist(),
    }
