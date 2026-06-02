"""Logging setup for V1."""

import logging
from pathlib import Path


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_logger(name: str, log_file: str | Path | None = None) -> logging.Logger:
    """Return a logger configured for console and optional file output."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT)

    if not _has_handler(logger, logging.StreamHandler):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file is not None:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if not _has_file_handler(logger, log_path):
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


def build_log_path(config: dict) -> Path | None:
    """Build optional log file path from config."""
    logging_config = config.get("logging")
    if not isinstance(logging_config, dict):
        return None

    log_dir = logging_config.get("dir")
    log_file = logging_config.get("file")
    if not log_dir or not log_file:
        return None

    return Path(log_dir) / log_file


def _has_handler(logger: logging.Logger, handler_type: type[logging.Handler]) -> bool:
    return any(isinstance(handler, handler_type) for handler in logger.handlers)


def _has_file_handler(logger: logging.Logger, log_path: Path) -> bool:
    resolved_path = log_path.resolve()
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            if Path(handler.baseFilename).resolve() == resolved_path:
                return True
    return False
