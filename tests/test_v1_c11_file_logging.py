"""Tests for V1 file-based logging."""

import logging
from pathlib import Path

from app.train import LOGGER_NAME, _format_log_section
from app.utils.logger import build_log_path, get_logger


def _reset_logger(name: str) -> None:
    logger = logging.getLogger(name)
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)


def test_get_logger_writes_to_file(tmp_path):
    logger_name = "tests.v1.c11.file_logging"
    _reset_logger(logger_name)
    log_file = tmp_path / "logs" / "modelopslab.log"

    logger = get_logger(logger_name, log_file)
    logger.info("file logging smoke message")
    for handler in logger.handlers:
        handler.flush()

    assert log_file.exists()
    assert "file logging smoke message" in log_file.read_text(encoding="utf-8")


def test_get_logger_does_not_duplicate_file_handlers(tmp_path):
    logger_name = "tests.v1.c11.duplicate_handlers"
    _reset_logger(logger_name)
    log_file = tmp_path / "logs" / "modelopslab.log"

    logger = get_logger(logger_name, log_file)
    logger = get_logger(logger_name, log_file)
    logger.info("single file line")
    for handler in logger.handlers:
        handler.flush()

    content = log_file.read_text(encoding="utf-8")

    assert content.count("single file line") == 1


def test_build_log_path_from_config():
    config = {"logging": {"dir": "logs", "file": "modelopslab.log"}}

    log_path = build_log_path(config)

    assert log_path == Path("logs") / "modelopslab.log"


def test_build_log_path_missing_config_returns_none():
    assert build_log_path({}) is None


def test_training_logger_name_is_stable():
    assert LOGGER_NAME == "modelopslab.training"


def test_format_log_section_uses_readable_key_value_block():
    section = _format_log_section(
        "DATASET",
        {
            "rows": 20,
            "target": "churn",
        },
    )

    assert "[DATASET]" in section
    assert "rows   : 20" in section
    assert "target : churn" in section
