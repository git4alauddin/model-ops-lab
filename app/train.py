"""V1 training entrypoint for config and dataset validation."""

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from app.config import ConfigError, load_config
from app.pipeline.preprocessing import (
    identify_feature_types,
    PreprocessingError,
    split_features_target,
    split_train_test,
)
from app.utils.logger import get_logger


class DataError(ValueError):
    """Raised when dataset loading or validation fails."""


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
        dataset_path = config["dataset"]["path"]
        target_column = config["dataset"]["target_column"]
        test_size = config["training"]["test_size"]
        random_state = config["training"]["random_state"]

        dataframe = load_dataset(dataset_path)
        features, target = split_features_target(dataframe, target_column)
        x_train, x_test, y_train, y_test = split_train_test(
            features,
            target,
            test_size,
            random_state,
        )
        numeric_features, categorical_features = identify_feature_types(x_train)

        logger.info(
            "Dataset loaded successfully. rows=%s cols=%s target=%s",
            len(dataframe),
            len(dataframe.columns),
            target_column,
        )
        logger.info(
            "Feature-target split completed. feature_cols=%s target_rows=%s",
            len(features.columns),
            len(target),
        )
        logger.info(
            "Train-test split completed. train_rows=%s test_rows=%s test_size=%s random_state=%s",
            len(x_train),
            len(x_test),
            test_size,
            random_state,
        )
        logger.info(
            "Feature type detection completed. numeric_features=%s categorical_features=%s",
            len(numeric_features),
            len(categorical_features),
        )
        logger.info("Training bootstrap completed.")
    except (ConfigError, DataError, PreprocessingError) as exc:
        logger.exception("Training bootstrap failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
