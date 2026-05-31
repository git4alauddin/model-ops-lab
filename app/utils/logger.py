"""Logging setup scaffold for V1."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a basic logger instance.

    Structured logging enrichment is added in later chunks.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger(name)
