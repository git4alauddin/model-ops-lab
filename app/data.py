"""Shared dataset loading utilities."""

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


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
