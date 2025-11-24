"""
A helper module to handle logging format.
"""

import logging
from typing import override


class LoggingFormatter(logging.Formatter):
    """
    A simple class to configure logging foramt.
    """

    GREY: str = "\x1b[38;21m"
    YELLOW: str = "\x1b[33;21m"
    RED: str = "\x1b[31;21m"
    BOLD_RED: str = "\x1b[31;1m"
    GREEN: str = "\x1b[32;21m"
    RESET: str = "\x1b[0m"

    _format_str: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    _FORMATS: dict[int, str] = {
        logging.DEBUG: GREY + _format_str + RESET,
        logging.INFO: GREEN + _format_str + RESET,
        logging.WARNING: YELLOW + _format_str + RESET,
        logging.ERROR: RED + _format_str + RESET,
        logging.CRITICAL: BOLD_RED + _format_str + RESET,
    }

    @override
    def format(self, record: "logging.LogRecord") -> str:
        """
        Format a logging record.

        Args:
            record (logging.LogRecord): The log record to format

        Returns:
            str: Formatted string
        """

        log_fmt = self._FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)
