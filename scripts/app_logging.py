import logging
from logging.config import dictConfig

def configure_logging(level: int = logging.INFO) -> None:
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                "datefmt": "%H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": level,
            }
        },
        "root": {"handlers": ["console"], "level": level},
    })

def get_logger(name: str = "scripts") -> logging.Logger:
    return logging.getLogger(name)
