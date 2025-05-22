import logging
from contextvars import ContextVar

LOGGING_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOGGING_JSON_FORMAT = (
    "%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)d %(request_id)s %(message)s"
)
LOGGING_DATEFMT = "%d-%m-%Y %H:%M:%S"

request_id_var = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {
            "()": RequestIdFilter,
        },
    },
    "formatters": {
        "standard": {"format": LOGGING_FORMAT, "datefmt": LOGGING_DATEFMT},
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": LOGGING_JSON_FORMAT,
            "datefmt": LOGGING_DATEFMT,
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file_json": {
            "level": "DEBUG",
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/fastapi/app.log",
            "filters": ["request_id"],
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file_json"],
            "level": "DEBUG",
            "propagate": True,
        },
        "your_module_name": {
            "handlers": ["file_json"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
