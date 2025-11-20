import logging

from src import app_logging


def test_configure_logging_sets_root_level_and_handler():
    app_logging.configure_logging(level=logging.DEBUG)

    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG

    stream_handlers = [
        handler for handler in root_logger.handlers
        if isinstance(handler, logging.StreamHandler)
    ]
    assert stream_handlers

    assert any(handler.level == logging.DEBUG for handler in stream_handlers)


def test_get_logger_returns_named_logger():
    app_logging.configure_logging()

    name = "src.test.logger"
    logger = app_logging.get_logger(name)

    assert isinstance(logger, logging.Logger)
    assert logger.name == name

    logger.info("test message")