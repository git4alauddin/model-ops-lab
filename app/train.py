"""V1 training entrypoint for config and dataset validation."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from app.config import ConfigError, load_config
from app.evaluate import EvaluationError, evaluate_model
from app.pipeline.preprocessing import (
    build_preprocessing_pipeline,
    identify_feature_types,
    PreprocessingError,
    split_features_target,
    split_train_test,
)
from app.pipeline.trainer import (
    TrainingError,
    build_model,
    build_training_pipeline,
    train_model,
)
from app.utils.artifacts import (
    ArtifactError,
    build_artifact_paths,
    save_json,
    save_model,
)
from app.utils.logger import build_log_path, get_logger

LOGGER_NAME = "modelopslab.training"


class DataError(ValueError):
    """Raised when dataset loading or validation fails."""


def drop_configured_columns(
    dataframe: pd.DataFrame,
    drop_columns: list[str],
) -> pd.DataFrame:
    """Drop configured non-feature columns before training."""
    if not drop_columns:
        return dataframe

    missing_columns = [
        column for column in drop_columns if column not in dataframe.columns
    ]
    if missing_columns:
        raise DataError(f"Configured drop columns not found: {missing_columns}")

    return dataframe.drop(columns=drop_columns)


def load_dataset(dataset_path: str | Path) -> pd.DataFrame:
    """Load dataset from CSV with controlled failures."""
    path = Path(dataset_path)
    if not path.exists():
        raise DataError(f"Dataset file not found: {path}")

    try:
        dataframe = pd.read_csv(path)
    except (ParserError, EmptyDataError, UnicodeDecodeError) as exc:
        raise DataError(f"Dataset could not be parsed: {path}") from exc
    except OSError as exc:
        raise DataError(f"Dataset could not be read: {path}") from exc

    if dataframe.empty:
        raise DataError(f"Dataset is empty: {path}")

    return dataframe


def _format_log_section(title: str, values: dict[str, Any]) -> str:
    """Format a readable key-value section for runtime logs."""
    key_width = max(len(key) for key in values)
    lines = [f"[{title}]"]
    lines.extend(f"{key:<{key_width}} : {value}" for key, value in values.items())
    return "\n".join(lines)


def main() -> None:
    """Validate config and dataset readiness for the V1 training flow."""
    config_path = Path("configs/training.yaml")
    logger = get_logger(LOGGER_NAME)

    try:
        config = load_config(config_path)
        log_path = build_log_path(config)
        logger = get_logger(LOGGER_NAME, log_path)
        run_started_at = datetime.now(UTC).isoformat()
        logger.info(
            "===== RUN STARTED %s | workflow=training =====",
            run_started_at,
        )
        dataset_config = cast(dict[str, Any], config["dataset"])
        training_config = cast(dict[str, Any], config["training"])
        model_config = cast(dict[str, Any], config["model"])
        dataset_path = cast(str, dataset_config["path"])
        target_column = cast(str, dataset_config["target_column"])
        drop_columns = cast(list[str], dataset_config.get("drop_columns", []))
        test_size = cast(float, training_config["test_size"])
        random_state = cast(int, training_config["random_state"])

        dataframe = load_dataset(dataset_path)
        dataframe = drop_configured_columns(dataframe, drop_columns)
        features, target = split_features_target(dataframe, target_column)
        x_train, x_test, y_train, y_test = split_train_test(
            features,
            target,
            test_size,
            random_state,
        )
        numeric_features, categorical_features = identify_feature_types(x_train)
        preprocessing_pipeline = build_preprocessing_pipeline(
            numeric_features,
            categorical_features,
        )
        model = build_model(model_config)
        training_pipeline = build_training_pipeline(preprocessing_pipeline, model)
        fitted_pipeline, training_duration = train_model(
            training_pipeline,
            x_train,
            y_train,
        )
        metrics = evaluate_model(fitted_pipeline, x_test, y_test)
        artifact_paths = build_artifact_paths(config)
        metadata = {
            "generated_at": run_started_at,
            "dataset_path": dataset_path,
            "target_column": target_column,
            "dropped_columns": drop_columns,
            "rows": len(dataframe),
            "columns": len(dataframe.columns),
            "feature_columns": len(features.columns),
            "train_rows": len(x_train),
            "test_rows": len(x_test),
            "numeric_features": numeric_features,
            "categorical_features": categorical_features,
            "model_type": model_config["type"],
            "training_duration_seconds": training_duration,
        }

        save_model(fitted_pipeline, artifact_paths["model"])
        save_json(metrics, artifact_paths["metrics"])
        save_json(config, artifact_paths["config_snapshot"])
        save_json(metadata, artifact_paths["metadata"])

        logger.info(_format_log_section("RUNTIME", {"log_file": log_path}))
        logger.info(
            _format_log_section(
                "DATASET",
                {
                    "path": dataset_path,
                    "rows": len(dataframe),
                    "columns": len(dataframe.columns),
                    "target": target_column,
                    "dropped_columns": drop_columns,
                },
            )
        )
        logger.info(
            _format_log_section(
                "SPLIT",
                {
                    "feature_columns": len(features.columns),
                    "target_rows": len(target),
                    "train_rows": len(x_train),
                    "test_rows": len(x_test),
                    "train_targets": len(y_train),
                    "test_targets": len(y_test),
                    "test_size": test_size,
                    "random_state": random_state,
                },
            )
        )
        logger.info(
            _format_log_section(
                "FEATURES",
                {
                    "numeric_features": len(numeric_features),
                    "categorical_features": len(categorical_features),
                },
            )
        )
        logger.info(
            _format_log_section(
                "PREPROCESSING",
                {
                    "numeric_enabled": bool(numeric_features),
                    "categorical_enabled": bool(categorical_features),
                    "transformers": len(preprocessing_pipeline.transformers),
                },
            )
        )
        logger.info(
            _format_log_section(
                "MODEL",
                {
                    "type": model_config["type"],
                    "duration_seconds": f"{training_duration:.6f}",
                    "fitted_steps": len(fitted_pipeline.steps),
                },
            )
        )
        logger.info(
            _format_log_section(
                "EVALUATION",
                {
                    "accuracy": f"{metrics['accuracy']:.6f}",
                    "precision": f"{metrics['precision']:.6f}",
                    "recall": f"{metrics['recall']:.6f}",
                    "f1": f"{metrics['f1']:.6f}",
                    "confusion_matrix": metrics["confusion_matrix"],
                },
            )
        )
        logger.info(
            _format_log_section(
                "ARTIFACTS",
                {
                    "model": artifact_paths["model"],
                    "metrics": artifact_paths["metrics"],
                    "config_snapshot": artifact_paths["config_snapshot"],
                    "metadata": artifact_paths["metadata"],
                },
            )
        )
        logger.info("Training bootstrap completed.")
    except (
        ArtifactError,
        ConfigError,
        DataError,
        EvaluationError,
        PreprocessingError,
        TrainingError,
    ) as exc:
        logger.exception("Training bootstrap failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
