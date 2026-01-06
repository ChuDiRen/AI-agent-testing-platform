"""
Logging Configuration and Error Handling Module

Provides centralized logging setup and error handling utilities.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
import traceback as tb
import json

from api_agent import settings


class ColorFormatter(logging.Formatter):
    """Colored log formatter for console output"""

    # Color codes
    GREY = '\x1b[38;21m'
    BLUE = '\x1b[38;5;39m'
    YELLOW = '\x1b[33;1m'
    RED = '\x1b[31;1m'
    MAGENTA = '\x1b[35;1m'
    GREEN = '\x1b[32;1m'
    RESET = '\x1b[0m'

    COLORS = {
        logging.DEBUG: GREY,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with color"""
        log_color = self.COLORS.get(record.levelno, self.GREY)
        record.levelname = record.levelname.ljust(8)

        # Format: timestamp [level] module - message
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        return f"{log_color}[{timestamp}]{self.RESET} {log_color}[{record.levelname}]{self.RESET} {log_color}{record.getMessage()}{self.RESET}"


class StructuredLogger:
    """
    Structured logger for consistent logging format

    Features:
    - JSON output for production
    - Colored console output for development
    - Context management
    - Error tracking
    """

    def __init__(self, name: str):
        """
        Initialize structured logger

        Args:
            name: Logger name (usually module name)
        """
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}

    def add_context(self, **kwargs):
        """
        Add context to logger

        Args:
            **kwargs: Context key-value pairs
        """
        self.context.update(kwargs)

    def clear_context(self):
        """Clear all context"""
        self.context.clear()

    def _format_message(self, msg: str, level: str = "info") -> str:
        """
        Format message with context

        Args:
            msg: Log message
            level: Log level

        Returns:
            Formatted message
        """
        if not self.context:
            return msg

        # Add context as structured data
        context_str = " | ".join([f"{k}={v}" for k, v in self.context.items()])
        return f"{msg} | {context_str}"

    def debug(self, msg: str, **kwargs):
        """Log debug message"""
        self.add_context(**kwargs)
        self.logger.debug(self._format_message(msg, "debug"))

    def info(self, msg: str, **kwargs):
        """Log info message"""
        self.add_context(**kwargs)
        self.logger.info(self._format_message(msg, "info"))

    def warning(self, msg: str, **kwargs):
        """Log warning message"""
        self.add_context(**kwargs)
        self.logger.warning(self._format_message(msg, "warning"))

    def error(self, msg: str, exc_info: Optional[Exception] = None, **kwargs):
        """
        Log error message

        Args:
            msg: Error message
            exc_info: Optional exception info
            **kwargs: Additional context
        """
        self.add_context(**kwargs)
        if exc_info:
            exc_str = f" {type(exc_info).__name__}: {str(exc_info)}"
            self.logger.error(self._format_message(msg + exc_str, "error"))
        else:
            self.logger.error(self._format_message(msg, "error"))

    def critical(self, msg: str, exc_info: Optional[Exception] = None, **kwargs):
        """Log critical message"""
        self.add_context(**kwargs)
        if exc_info:
            exc_str = f" {type(exc_info).__name__}: {str(exc_info)}"
            self.logger.critical(self._format_message(msg + exc_str, "critical"))
        else:
            self.logger.critical(self._format_message(msg, "critical"))

    def exception(self, exc: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Log exception with full traceback

        Args:
            exc: Exception object
            context: Optional additional context
        """
        self.error(
            msg="Exception occurred",
            exc_info=exc,
            **(context or {})
        )

        # Log full traceback at debug level
        tb_str = ''.join(tb.format_exception(type(exc), exc, exc, tb))
        self.logger.debug(f"Full traceback:\n{tb_str}")


class AppErrorHandler:
    """
    Application Error Handler

    Centralized error handling with:
    - Error categorization
    - Retry logic
    - Fallback mechanisms
    - Error reporting
    """

    ERROR_CATEGORIES = {
        "network": ["ConnectionError", "TimeoutError", "HTTPError"],
        "authentication": ["AuthenticationError", "Unauthorized"],
        "validation": ["ValidationError", "ValueError"],
        "execution": ["ExecutionError", "RuntimeError"],
        "mcp": ["MCPError", "MCPConnectionError"]
    }

    def __init__(self, logger: StructuredLogger):
        """
        Initialize error handler

        Args:
            logger: Structured logger instance
        """
        self.logger = logger
        self.error_count: Dict[str, int] = {}

    def categorize_error(self, exc: Exception) -> str:
        """
        Categorize error type

        Args:
            exc: Exception to categorize

        Returns:
            Error category (network, authentication, validation, execution, mcp, unknown)
        """
        exc_name = type(exc).__name__

        for category, exceptions in self.ERROR_CATEGORIES.items():
            if exc_name in exceptions or isinstance(exc, tuple(exceptions)):
                return category

        return "unknown"

    def handle_error(
        self,
        exc: Exception,
        context: Optional[Dict[str, Any]] = None,
        raise_exception: bool = True
    ) -> Optional[Any]:
        """
        Handle error with logging and optional exception re-raising

        Args:
            exc: Exception to handle
            context: Optional error context
            raise_exception: Whether to re-raise exception

        Returns:
            Optional fallback value
        """
        category = self.categorize_error(exc)

        # Track error count
        exc_name = type(exc).__name__
        self.error_count[exc_name] = self.error_count.get(exc_name, 0) + 1

        # Log error
        self.logger.error(
            msg=f"Error [{category}]: {str(exc)}",
            exc_info=exc,
            category=category,
            error_count=self.error_count[exc_name],
            **(context or {})
        )

        # Determine if should retry or fallback
        should_retry = category in ["network", "mcp"] and self.error_count[exc_name] < 3

        if should_retry and not raise_exception:
            # Return None to indicate retry should be attempted
            return None

        if raise_exception:
            raise

        return None

    def get_error_stats(self) -> Dict[str, Any]:
        """
        Get error statistics

        Returns:
            Dictionary with error counts by type
        """
        total_errors = sum(self.error_count.values())
        category_counts = {}

        for exc_name, count in self.error_count.items():
            category = self.categorize_error(type(exc_name, Exception))
            category_counts[category] = category_counts.get(category, 0) + count

        return {
            "total_errors": total_errors,
            "by_type": self.error_count.copy(),
            "by_category": category_counts
        }


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    json_output: bool = False
) -> None:
    """
    Setup logging for the application

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        json_output: Whether to output JSON format
    """
    # Determine log level from settings or parameter
    log_level = level or settings.log_level.upper() if hasattr(settings, 'log_level') else "INFO"

    # Convert string to logging level
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()

    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    if json_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(message)s'))
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColorFormatter())

    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(numeric_level)

        if json_output:
            file_handler.setFormatter(logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s"}'
            ))
        else:
            file_handler.setFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

        root_logger.addHandler(file_handler)
    else:
        # Default file logging
        log_file_path = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(numeric_level)

        if json_output:
            file_handler.setFormatter(logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s"}'
            ))
        else:
            file_handler.setFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

        root_logger.addHandler(file_handler)

    # Silence noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)

    logging.info(f"Logging initialized at level: {log_level}")


def get_logger(name: str) -> StructuredLogger:
    """
    Get or create a structured logger

    Args:
        name: Logger name (usually module name)

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


def get_error_handler(logger: StructuredLogger) -> AppErrorHandler:
    """
    Get or create error handler

    Args:
        logger: Structured logger instance

    Returns:
        AppErrorHandler instance
    """
    return AppErrorHandler(logger)


class RequestContext:
    """
    Request context manager for logging

    Adds request ID and user ID to all logs within context.

    Usage:
        ```python
        with RequestContext(request_id="req_123", user_id="user_456"):
            logger.info("Processing request")
        ```
    """

    def __init__(self, **context):
        """
        Initialize request context

        Args:
            **context: Context key-value pairs (request_id, user_id, session_id, etc.)
        """
        self.context = context
        self.loggers = []

    def __enter__(self):
        """Enter context, add to all loggers"""
        # Get all active loggers
        logger_dict = logging.getLogger().manager.loggerDict

        for name, logger in logger_dict.items():
            if isinstance(logger, StructuredLogger):
                logger.add_context(**self.context)
                self.loggers.append(logger)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context, clear from all loggers"""
        for logger in self.loggers:
            logger.clear_context()

        return False
