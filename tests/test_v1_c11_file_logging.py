"""Tests for V1 file-based logging."""

import logging

from app.utils.logger import build_log_path, get_logger


def _reset_logger(name: str) -> None:
    logger = logging.getLogger(name)
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)


def test_get_logger_writes_to_file(tmp_path):
    logger_name = "tests.v1.c11.file_logging"
    _reset_logger(logger_name)
    log_file = tmp_path / "logs" / "training.log"

    logger = get_logger(logger_name, log_file)
    logger.info("file logging smoke message")
    for handler in logger.handlers:
        handler.flush()

    assert log_file.exists()
    assert "file logging smoke message" in log_file.read_text(encoding="utf-8")


def test_get_logger_does_not_duplicate_file_handlers(tmp_path):
    logger_name = "tests.v1.c11.duplicate_handlers"
    _reset_logger(logger_name)
    log_file = tmp_path / "logs" / "training.log"

    logger = get_logger(logger_name, log_file)
    logger = get_logger(logger_name, log_file)
    logger.info("single file line")
    for handler in logger.handlers:
        handler.flush()

    content = log_file.read_text(encoding="utf-8")

    assert content.count("single file line") == 1


def test_build_log_path_from_config():
    config = {"logging": {"dir": "logs", "file": "training.log"}}

    log_path = build_log_path(config)

    assert str(log_path) == "logs\\training.log"


def test_build_log_path_missing_config_returns_none():
    assert build_log_path({}) is None
