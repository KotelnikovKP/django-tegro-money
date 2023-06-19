import os
import logging
import logging.config
import time

FOLDER_LOG = "tegro_money_log"


def create_log_folder(folder=FOLDER_LOG):
    if not os.path.exists(folder):
        os.mkdir(folder)


class MyStreamHandler(logging.StreamHandler):
    def emit(self, record):
        level_no = record.levelno
        if level_no >= 50:
            color = '\x1b[31m'  # red
        elif level_no >= 40:
            color = '\x1b[31m'  # red
        elif level_no >= 30:
            color = '\x1b[33m'  # yellow
        elif level_no >= 20:
            color = '\x1b[32m'  # green
        elif level_no >= 10:
            color = '\x1b[35m'  # pink
        else:
            color = '\x1b[0m'  # normal
        previous_msg = record.msg
        record.msg = color + record.msg + '\x1b[0m'
        super(MyStreamHandler, self).emit(record)
        record.msg = previous_msg


def get_logger() -> logging.Logger:

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "\x1b[37m%(asctime)s.%(msecs)03d %(module)s:%(funcName)s:%(lineno)d %(levelname)s | \x1b[0m"
                          "%(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "rotating_file": {
                "format": "%(asctime)s.%(msecs)03d %(module)s:%(funcName)s:%(lineno)d %(levelname)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "django_tegro_money.loggers.MyStreamHandler",
                "level": "INFO",
                "formatter": "console",
            },
            "rotating_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "rotating_file",
                "filename": "tegro_money_log/main.log",
                "maxBytes": 10485760,
                "backupCount": 200,
            }
        },
        "loggers": {
            "default": {
                "handlers": ["console", "rotating_file"],
                "level": "DEBUG"
            }
        }
    }
    create_log_folder()
    logging.Formatter.converter = time.gmtime
    logging.config.dictConfig(log_config)
    return logging.getLogger("default")
