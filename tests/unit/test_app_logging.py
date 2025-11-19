import logging

from src import app_logging


def test_configure_logging_sets_root_level_and_handler():
    # Call with a non-default level so it's easy to check
    app_logging.configure_logging(level=logging.DEBUG)

    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG

    # There is a StreamHandler attached
    stream_handlers = [
        handler for handler in root_logger.handlers
        if isinstance(handler, logging.StreamHandler)
    ]
    assert stream_handlers  # not empty

    # And one of them should have level DEBUG
    assert any(handler.level == logging.DEBUG for handler in stream_handlers)


def test_get_logger_returns_named_logger():
    app_logging.configure_logging()  # ensure logging is configured

    name = "src.test.logger"
    logger = app_logging.get_logger(name)

    assert isinstance(logger, logging.Logger)
    assert logger.name == name

    # Check that logging through this logger does not raise
    logger.info("test message")