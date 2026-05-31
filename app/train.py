"""V1 training entrypoint for config and dataset validation."""

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from app.config import ConfigError, load_config
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

        dataframe = load_dataset(dataset_path)
        if target_column not in dataframe.columns:
            raise DataError(f"Target column '{target_column}' not found in dataset.")

        logger.info(
            "Dataset loaded successfully. rows=%s cols=%s target=%s",
            len(dataframe),
            len(dataframe.columns),
            target_column,
        )
        logger.info("Training bootstrap completed.")
    except (ConfigError, DataError) as exc:
        logger.exception("Training bootstrap failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
