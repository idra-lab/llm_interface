"""Logging utilities with compact console and rotating-file output."""

import logging
import os
import re
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Mapping, Union

try:
    from loguru import logger as _loguru_logger
except Exception:
    _loguru_logger = None


ITALIC = "\033[3m"
BOLD = "\033[1m"
RESET = "\033[0m"
RED = "\033[91m"
FILE_NAME_WIDTH = 30


def bold(text: str) -> str:
    """Return text wrapped in ANSI bold escape codes.

    Parameters
    ----------
    text : str
        Text to format.

    Returns
    -------
    str
        Formatted text.
    """
    return f"{BOLD}{text}{RESET}"


def italic(text: str) -> str:
    """Return text wrapped in ANSI italic escape codes.

    Parameters
    ----------
    text : str
        Text to format.

    Returns
    -------
    str
        Formatted text.
    """
    return f"{ITALIC}{text}{RESET}"


LEVEL_NAME_MAP = {
    "DEBUG": "DBG",
    "INFO": "INF",
    "WARNING": "WRN",
    "ERROR": "ERR",
    "CRITICAL": "CRT",
}

# Same shape as the tags Loguru parses (loguru/_colorizer.py); only these need escaping.
ANGULAR_BRACKETS_PATTERN = re.compile(r"</?(?:[fb]g\s)?[^<>\s]*>")
CURLY_BRACKETS_PATTERN = re.compile(r"\{.*?\}", re.DOTALL)


def _short_level_name(level_name: str) -> str:
    short_name = LEVEL_NAME_MAP.get(level_name, level_name)
    if short_name in {"ERR", "CRT"}:
        return f"{RED}{short_name}{RESET}"
    return short_name


def _format_time(record_time: datetime) -> str:
    return record_time.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]


def _escape_braces(text: str) -> str:
    # Escape braces for Loguru formatting and angle brackets for markup safety.

    # A backslash before anything that is not a tag would be printed as-is.
    text = ANGULAR_BRACKETS_PATTERN.sub(lambda match: "\\" + match.group(0), text)

    match = CURLY_BRACKETS_PATTERN.search(text)
    if match:
        text = text.replace("{", "{{").replace("}", "}}")

    return text


def _format_console(record: Mapping[str, Any]) -> str:
    level = _short_level_name(record["level"].name)
    message = _escape_braces(record["message"])
    return f"[{BOLD}{level}{RESET}] {message}\n"


def _format_file(record: Mapping[str, Any]) -> str:
    time_str = _format_time(record["time"])
    level = _short_level_name(record["level"].name)
    message = _escape_braces(record["message"])
    # Placeholder names like "<string>" (python -c, REPL, notebooks) would read as color tags.
    file_name = _escape_braces(f"{record['file'].name:<{FILE_NAME_WIDTH}}")
    return f"{time_str} {ITALIC}{file_name}{RESET} [{BOLD}{level}{RESET}] {message}\n"


class ShortLevelFormatter(logging.Formatter):
    """Formatter that replaces standard log levels with compact names."""

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with a shortened level name.

        Parameters
        ----------
        record : logging.LogRecord
            Log record to format.

        Returns
        -------
        str
            Formatted log record.
        """
        original_levelname = record.levelname
        record.levelname = _short_level_name(original_levelname)
        try:
            return super().format(record)
        finally:
            record.levelname = original_levelname


class Logger(logging.Logger):
    """Logger with compact level names and optional Loguru support."""

    def __init__(self, name: str, output_dir: str = ".", output_file_name: str = "log.log") -> None:
        """Initialize the logger.

        Parameters
        ----------
        name : str
            Logger name.
        output_dir : str, optional
            Directory for the rotating log file.
        output_file_name : str, optional
            Log file name.
        """
        assert os.path.exists(output_dir), f"{output_dir} does not exist, create it first"
        super().__init__(name)
        self._use_loguru = _loguru_logger is not None
        self._output_dir = output_dir
        self._output_file_name = output_file_name
        self._max_bytes = 200 * 1024
        self._loguru_sinks = []
        super().setLevel(logging.DEBUG)

        if _loguru_logger is not None:
            self._loguru = _loguru_logger.bind(logger_name=name)
            self._configure_loguru()
        else:
            # Create handlers
            self.c_handler = logging.StreamHandler()
            self.f_handler = RotatingFileHandler(
                os.path.join(output_dir, output_file_name),
                maxBytes=self._max_bytes,
                backupCount=1,
            )
            self.c_handler.setLevel(self.level)
            self.f_handler.setLevel(self.level)
            # Create formatters and add them to handlers
            self.c_format = ShortLevelFormatter(f"[{BOLD}%(levelname)s{RESET}] %(message)s")
            self.f_format = ShortLevelFormatter(
                f"%(asctime)s {ITALIC}%(filename)s{RESET} [{BOLD}%(levelname)s{RESET}] %(message)s"
            )
            self.c_handler.setFormatter(self.c_format)
            self.f_handler.setFormatter(self.f_format)
            # Add handlers to the logger
            self.addHandler(self.c_handler)
            self.addHandler(self.f_handler)

    def _configure_loguru(self) -> None:
        """Configure Loguru sinks for console and rotating-file output."""
        # Remove default and previously-added sinks to enforce our formatting.
        self._loguru.remove()
        self._loguru_sinks = []
        level_name = logging.getLevelName(self.level)
        self._loguru_sinks.append(
            self._loguru.add(
                sys.stderr,
                level=level_name,
                format=_format_console,
                colorize=False,
                backtrace=False,
                diagnose=False,
            )
        )
        self._loguru_sinks.append(
            self._loguru.add(
                os.path.join(self._output_dir, self._output_file_name),
                level=level_name,
                format=_format_file,
                rotation=self._max_bytes,
                retention=1,
                colorize=False,
                backtrace=False,
                diagnose=False,
            )
        )

    def _log(
        self,
        level: int,
        msg: object,
        args: Any,
        exc_info: Any = None,
        extra: Union[Mapping[str, object], None] = None,
        stack_info: bool = False,
        stacklevel: int = 1,
    ) -> None:
        """Log a message through Loguru when available, otherwise stdlib logging.

        Parameters
        ----------
        level : int
            Logging level.
        msg : str
            Log message.
        args : tuple
            Positional formatting arguments for ``msg``.
        exc_info : object, optional
            Exception information.
        extra : dict, optional
            Extra logging fields.
        stack_info : bool, optional
            Whether to include stack information.
        stacklevel : int, optional
            Stack level used to resolve the caller.
        """
        if self._use_loguru:
            level_name = logging.getLevelName(level)
            if args:
                msg = str(msg) % args
                args = ()
            depth = 2 + max(stacklevel - 1, 0)
            self._loguru.opt(depth=depth, exception=exc_info).log(level_name, msg, *args)
            return
        super()._log(
            level,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    def setLevel(self, level: Union[int, str]) -> None:
        """Set the logger level and update handlers.

        Parameters
        ----------
        level : int or str
            Logging level accepted by ``logging.Logger.setLevel``.
        """
        super().setLevel(level)
        if self._use_loguru:
            self._configure_loguru()
        else:
            for handler in self.handlers:
                handler.setLevel(level)

    def set_debug(self) -> None:
        """Set the logger to debug mode."""
        self.setLevel(logging.DEBUG)

    def set_info(self) -> None:
        """Set the logger to info mode."""
        self.setLevel(logging.INFO)

    def set_warning(self) -> None:
        """Set the logger to warning mode."""
        self.setLevel(logging.WARNING)

    def set_error(self) -> None:
        """Set the logger to error mode."""
        self.setLevel(logging.ERROR)

    def set_critical(self) -> None:
        """Set the logger to critical mode."""
        self.setLevel(logging.CRITICAL)

    def change_output_dir_file(self, output_dir: str, output_file: str) -> None:
        """Change the rotating log file location.

        Parameters
        ----------
        output_dir : str
            Directory containing the new log file.
        output_file : str
            New log file name.
        """
        self._output_dir = output_dir
        self._output_file_name = output_file
        if self._use_loguru:
            self._configure_loguru()
        else:
            new_handler = RotatingFileHandler(
                os.path.join(output_dir, output_file),
                maxBytes=self._max_bytes,
                backupCount=1,
            )
            new_handler.setLevel(self.f_handler.level)
            new_handler.setFormatter(self.f_format)
            self.removeHandler(self.f_handler)
            self.f_handler = new_handler
            self.addHandler(self.f_handler)


logger = Logger(Path(__file__).parent.name)
