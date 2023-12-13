import logging
from os import environ

from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger

# Determine if DEBUG logging should be enabled
load_dotenv()
debug = environ.get("FLASK_DEBUG", default=False)


def create_logger(name):
    """
    Returns a logger with the given name
    """
    logger = logging.getLogger(name)
    logHandler = logging.StreamHandler()
    logHandler.setFormatter(json_formatter)
    logger.addHandler(logHandler)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    return logger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    As long as https://github.com/madzak/python-json-logger/issues/171 is still open,
    we need to have our own JsonFormatter implementation that fixes the bug.
    """

    def _perform_rename_log_fields(self, log_record):
        for old_field_name, new_field_name in self.rename_fields.items():
            if old_field_name not in log_record:
                continue
            log_record[new_field_name] = log_record[old_field_name]
            del log_record[old_field_name]


reserved_attrs = [
    'taskName', 'args', 'levelno', 'pathname', 'name', 'msg', 'module',
    'exc_info', 'exc_text', 'stack_info', 'created', 'relativeCreated', 'msecs',
    'thread', 'threadName', 'processName', 'process',
]

json_formatter = CustomJsonFormatter(
    json_indent=4,
    timestamp=True,
    reserved_attrs=reserved_attrs,
    rename_fields={'levelname': 'level'},
)
