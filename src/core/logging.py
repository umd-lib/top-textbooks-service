import logging
import sys
from os import environ

from pythonjsonlogger import jsonlogger


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


class RedactingFilter(logging.Filter):
    """
    Logging Filter implementation that replaces specific strings with
    "[REDACTED]".

    Primarily intended to prevent API keys from appearing in log messages.

    This filter redacts based on exact string matches (*not* regular
    expressions).

    Inspired (and largely taken from
    https://relaxdiego.com/2014/07/logging-in-python.html)
    """
    def __init__(self, patterns):
        super(RedactingFilter, self).__init__()
        self._patterns = patterns

    def filter(self, record):
        record.msg = self.redact(record.msg)
        if isinstance(record.args, dict):
            for k in record.args.keys():
                record.args[k] = self.redact(record.args[k])
        else:
            record.args = tuple(self.redact(arg) for arg in record.args)
        return True

    def redact(self, msg):
        msg = isinstance(msg, str) and msg or str(msg)
        for pattern in self._patterns:
            msg = msg.replace(pattern, "[REDACTED]")
        return msg


# Determine if DEBUG logging should be enabled
debug = environ.get("FLASK_DEBUG", default=False)

# Retrieve API key for redaction
log_redacting_filter = None

log_redaction_key = environ.get('LOG_REDACTION_KEY', None)
if log_redaction_key:
    log_redaction_value = environ.get(log_redaction_key)
    log_redacting_filter = RedactingFilter([log_redaction_value])

reserved_attrs = [
    'taskName', 'args', 'levelno', 'pathname', 'name', 'msg', 'module',
    'exc_info', 'exc_text', 'stack_info', 'created', 'relativeCreated', 'msecs',
    'thread', 'threadName', 'processName', 'process',
]

json_formatter = CustomJsonFormatter(
    timestamp=True,
    reserved_attrs=reserved_attrs,
    rename_fields={'levelname': 'level'},
)


def create_logger(name):
    """
    Returns a logger with the given name
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logHandler = logging.StreamHandler()

    if log_redacting_filter:
        logHandler.addFilter(log_redacting_filter)

    # When running tests, do not want to use the JSON logger
    is_pytest_running = ("pytest" in sys.modules)

    use_json_logger = not (debug or is_pytest_running)
    if use_json_logger:
        logHandler.setFormatter(json_formatter)
        logger.setLevel(logging.INFO)

        # Disable doubling logging in production.
        #
        # The root logger logs the same information as the generated ones,
        # without the formatting.
        #
        # Pytest depends on capturing log information from the root logger.
        #
        # Since testing would be done during development, and since we would
        # probably be debugging at the same time, setting logger.propagate to
        # false during development seems like the least intrusive change.
        logger.propagate = False

    logger.addHandler(logHandler)
    return logger
