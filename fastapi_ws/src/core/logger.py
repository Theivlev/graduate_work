LOGGING_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOGGING_VERBOSE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s " "%(funcName)s:%(lineno)d: %(message)s"
LOGGING_DATEFMT = "%d-%m-%Y %H:%M:%S"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": LOGGING_FORMAT, "datefmt": LOGGING_DATEFMT},
        "verbose": {"format": LOGGING_VERBOSE_FORMAT, "datefmt": LOGGING_DATEFMT},
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "level": "DEBUG",
            "formatter": "verbose",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "your_module_name": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
