"""Structured logging configuration for Cloud Logging compatibility.

This module provides JSON-formatted logging output compatible with Google Cloud Logging.
When deployed to Cloud Run, logs are automatically ingested by Cloud Logging with
proper severity levels and structured metadata.

Cloud Logging Severity Levels:
- DEBUG: Debug or trace information
- INFO: Routine information
- WARNING: Warning events that might cause problems
- ERROR: Error events that might still allow the application to continue
- CRITICAL: Critical events that cause the application to fail

Reference: https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#LogSeverity
"""

import json
import logging
import sys
import traceback
from datetime import datetime, timezone
from typing import Any


# Cloud Logging severity level mapping
# Maps Python logging levels to Cloud Logging severity strings
CLOUD_LOGGING_SEVERITY = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.WARNING: "WARNING",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRITICAL",
}


class CloudLoggingFormatter(logging.Formatter):
    """JSON formatter compatible with Google Cloud Logging.
    
    Outputs log records as JSON objects with fields that Cloud Logging
    recognizes for proper severity mapping and structured data.
    
    Output format:
    {
        "severity": "INFO",
        "message": "Log message",
        "timestamp": "2024-01-01T00:00:00.000000Z",
        "logger": "module.name",
        "module": "filename",
        "function": "function_name",
        "line": 42,
        "stack_trace": "..." (only for ERROR and above)
    }
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string.
        
        Args:
            record: The log record to format.
            
        Returns:
            JSON-formatted string suitable for Cloud Logging.
        """
        # Build the base log entry
        log_entry: dict[str, Any] = {
            "severity": CLOUD_LOGGING_SEVERITY.get(record.levelno, "DEFAULT"),
            "message": record.getMessage(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info for errors
        if record.exc_info and record.levelno >= logging.ERROR:
            log_entry["stack_trace"] = self._format_exception(record.exc_info)
        
        # Add any extra fields from the record
        # This allows passing additional context via extra={} in log calls
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)

    def _format_exception(self, exc_info: tuple) -> str:
        """Format exception info as a string.
        
        Args:
            exc_info: Exception info tuple from sys.exc_info().
            
        Returns:
            Formatted stack trace string.
        """
        if exc_info[0] is None:
            return ""
        return "".join(traceback.format_exception(*exc_info))


class StandardFormatter(logging.Formatter):
    """Standard human-readable formatter for local development.
    
    Provides colored, readable output for local development while
    maintaining the same information as the JSON formatter.
    """

    FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
    
    def __init__(self) -> None:
        super().__init__(fmt=self.FORMAT, datefmt="%Y-%m-%d %H:%M:%S")


def configure_logging(
    level: int = logging.INFO,
    json_format: bool = True,
    logger_name: str | None = None,
) -> logging.Logger:
    """Configure logging with Cloud Logging compatible format.
    
    Args:
        level: Logging level (default: INFO).
        json_format: If True, use JSON format for Cloud Logging.
                    If False, use human-readable format for local dev.
        logger_name: Optional specific logger name. If None, configures root logger.
        
    Returns:
        Configured logger instance.
        
    Example:
        # For production (Cloud Run)
        logger = configure_logging(json_format=True)
        
        # For local development
        logger = configure_logging(json_format=False)
        
        # Log with extra context
        logger.info("Request processed", extra={"extra_fields": {"request_id": "123"}})
    """
    # Get or create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create handler for stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Set formatter based on environment
    if json_format:
        handler.setFormatter(CloudLoggingFormatter())
    else:
        handler.setFormatter(StandardFormatter())
    
    logger.addHandler(handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


def setup_application_logging(app_env: str = "development") -> None:
    """Set up application-wide logging configuration.
    
    Configures the root logger and common library loggers based on
    the application environment.
    
    Args:
        app_env: Application environment ("development", "staging", "production").
    """
    # Use JSON format in production/staging, human-readable in development
    use_json = app_env in ("production", "staging")
    
    # Set log level based on environment
    log_level = logging.DEBUG if app_env == "development" else logging.INFO
    
    # Configure root logger
    configure_logging(level=log_level, json_format=use_json)
    
    # Configure specific loggers for common libraries
    # Reduce noise from verbose libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.
    
    This is a convenience function that returns a logger configured
    to work with the application's logging setup.
    
    Args:
        name: Logger name, typically __name__ of the calling module.
        
    Returns:
        Logger instance.
        
    Example:
        from backend.utils.logging import get_logger
        
        logger = get_logger(__name__)
        logger.info("Processing request")
    """
    return logging.getLogger(name)


def log_error_with_context(
    logger: logging.Logger,
    message: str,
    error: Exception,
    **context: Any,
) -> None:
    """Log an error with additional context information.
    
    This helper function logs errors with structured context that
    Cloud Logging can parse and index.
    
    Args:
        logger: Logger instance to use.
        message: Error message.
        error: The exception that occurred.
        **context: Additional context key-value pairs.
        
    Example:
        try:
            process_request(request_id)
        except Exception as e:
            log_error_with_context(
                logger,
                "Failed to process request",
                e,
                request_id=request_id,
                user_id=user_id,
            )
    """
    extra_fields = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        **context,
    }
    logger.error(message, exc_info=True, extra={"extra_fields": extra_fields})
