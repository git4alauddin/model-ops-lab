"""V1 training entrypoint for config and dataset validation."""

from pathlib import Path
from typing import Any, cast

import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from app.config import ConfigError, load_config
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
from app.utils.logger import get_logger


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


def main() -> None:
    """Validate config and dataset readiness for the V1 training flow."""
    logger = get_logger(__name__)
    config_path = Path("configs/training.yaml")

    try:
        logger.info("Training bootstrap started.")
        config = load_config(config_path)
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

        logger.info(
            "Dataset loaded successfully. rows=%s cols=%s target=%s",
            len(dataframe),
            len(dataframe.columns),
            target_column,
        )
        logger.info("Dropped configured columns. columns=%s", drop_columns)
        logger.info(
            "Feature-target split completed. feature_cols=%s target_rows=%s",
            len(features.columns),
            len(target),
        )
        logger.info(
            (
                "Train-test split completed. train_rows=%s test_rows=%s "
                "train_targets=%s test_targets=%s test_size=%s random_state=%s"
            ),
            len(x_train),
            len(x_test),
            len(y_train),
            len(y_test),
            test_size,
            random_state,
        )
        logger.info(
            (
                "Feature type detection completed. numeric_features=%s "
                "categorical_features=%s"
            ),
            len(numeric_features),
            len(categorical_features),
        )
        logger.info(
            (
                "Preprocessing pipeline created. numeric_enabled=%s "
                "categorical_enabled=%s transformers=%s"
            ),
            bool(numeric_features),
            bool(categorical_features),
            len(preprocessing_pipeline.transformers),
        )
        logger.info(
            (
                "Model training completed. model_type=%s "
                "duration_seconds=%.6f fitted_steps=%s"
            ),
            model_config["type"],
            training_duration,
            len(fitted_pipeline.steps),
        )
        logger.info("Training bootstrap completed.")
    except (ConfigError, DataError, PreprocessingError, TrainingError) as exc:
        logger.exception("Training bootstrap failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
