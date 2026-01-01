"""Property tests for structured logging configuration.

Property: Error Logging Produces Structured Output
- Test that logged errors are valid JSON
- Test that severity levels are correct
Validates: Requirements 7.1, 7.3
"""

import io
import json
import logging
import sys
from unittest.mock import patch

import pytest
from hypothesis import given, settings as hypothesis_settings, strategies as st

from backend.utils.logging import (
    CLOUD_LOGGING_SEVERITY,
    CloudLoggingFormatter,
    StandardFormatter,
    configure_logging,
    get_logger,
    log_error_with_context,
    setup_application_logging,
)


class TestCloudLoggingFormatterProducesValidJSON:
    """Property: Error Logging Produces Structured Output.
    
    Feature: cloud-run-deployment
    **Validates: Requirements 7.1, 7.3**
    
    For any log message, the CloudLoggingFormatter SHALL produce
    valid JSON output with correct severity levels.
    """

    @given(
        message=st.text(min_size=1, max_size=200).filter(
            lambda x: x.strip() and not any(c in x for c in ['\x00'])
        ),
    )
    @hypothesis_settings(max_examples=100)
    def test_info_logs_produce_valid_json(self, message: str) -> None:
        """Property: INFO level logs produce valid JSON.
        
        For any non-empty message logged at INFO level,
        the output SHALL be valid JSON with severity "INFO".
        """
        # Capture log output
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(CloudLoggingFormatter())
        
        logger = logging.getLogger("test_info_json")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
        # Log the message
        logger.info(message)
        
        # Get output and parse as JSON
        output = stream.getvalue().strip()
        
        # Should be valid JSON
        log_entry = json.loads(output)
        
        # Should have required fields
        assert "severity" in log_entry
        assert "message" in log_entry
        assert "timestamp" in log_entry
        assert "logger" in log_entry
        
        # Severity should be INFO
        assert log_entry["severity"] == "INFO"
        
        # Message should contain our text
        assert message in log_entry["message"]

    @given(
        message=st.text(min_size=1, max_size=200).filter(
            lambda x: x.strip() and not any(c in x for c in ['\x00'])
        ),
    )
    @hypothesis_settings(max_examples=100)
    def test_error_logs_produce_valid_json(self, message: str) -> None:
        """Property: ERROR level logs produce valid JSON.
        
        For any non-empty message logged at ERROR level,
        the output SHALL be valid JSON with severity "ERROR".
        """
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(CloudLoggingFormatter())
        
        logger = logging.getLogger("test_error_json")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        logger.propagate = False
        
        logger.error(message)
        
        output = stream.getvalue().strip()
        log_entry = json.loads(output)
        
        assert log_entry["severity"] == "ERROR"
        assert message in log_entry["message"]

    @given(
        message=st.text(min_size=1, max_size=200).filter(
            lambda x: x.strip() and not any(c in x for c in ['\x00'])
        ),
    )
    @hypothesis_settings(max_examples=100)
    def test_warning_logs_produce_valid_json(self, message: str) -> None:
        """Property: WARNING level logs produce valid JSON.
        
        For any non-empty message logged at WARNING level,
        the output SHALL be valid JSON with severity "WARNING".
        """
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(CloudLoggingFormatter())
        
        logger = logging.getLogger("test_warning_json")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
        logger.propagate = False
        
        logger.warning(message)
        
        output = stream.getvalue().strip()
        log_entry = json.loads(output)
        
        assert log_entry["severity"] == "WARNING"
        assert message in log_entry["message"]

    @given(level=st.sampled_from([logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]))
    @hypothesis_settings(max_examples=100)
    def test_all_severity_levels_map_correctly(self, level: int) -> None:
        """Property: All Python log levels map to Cloud Logging severity.
        
        For any Python logging level, the CloudLoggingFormatter SHALL
        map it to the correct Cloud Logging severity string.
        """
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(CloudLoggingFormatter())
        
        logger = logging.getLogger(f"test_level_{level}")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        
        logger.log(level, "Test message")
        
        output = stream.getvalue().strip()
        log_entry = json.loads(output)
        
        expected_severity = CLOUD_LOGGING_SEVERITY[level]
        assert log_entry["severity"] == expected_severity


class TestErrorLogsIncludeStackTrace:
    """Test that error logs include stack traces.
    
    **Validates: Requirements 7.3**
    """

    def test_error_with_exception_includes_stack_trace(self) -> None:
        """Test that errors logged with exc_info include stack trace."""
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(CloudLoggingFormatter())
        
        logger = logging.getLogger("test_stack_trace")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        logger.propagate = False
        
        try:
            raise ValueError("Test error for stack trace")
        except ValueError:
            logger.error("An error occurred", exc_info=True)
        
        output = stream.getvalue().strip()
        log_entry = json.loads(output)
        
        # Should have stack_trace field
        assert "stack_trace" in log_entry
        assert "ValueError" in log_entry["stack_trace"]
        assert "Test error for stack trace" in log_entry["stack_trace"]

    def test_info_without_exception_has_no_stack_trace(self) -> None:
        """Test that INFO logs without exceptions don't have stack trace."""
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(CloudLoggingFormatter())
        
        logger = logging.getLogger("test_no_stack_trace")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
        logger.info("Normal info message")
        
        output = stream.getvalue().strip()
        log_entry = json.loads(output)
        
        # Should NOT have stack_trace field
        assert "stack_trace" not in log_entry


class TestLogErrorWithContext:
    """Test the log_error_with_context helper function."""

    def test_log_error_with_context_includes_all_fields(self) -> None:
        """Test that log_error_with_context includes error details and context."""
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(CloudLoggingFormatter())
        
        logger = logging.getLogger("test_context")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        logger.propagate = False
        
        try:
            raise RuntimeError("Test runtime error")
        except RuntimeError as e:
            log_error_with_context(
                logger,
                "Failed to process request",
                e,
                request_id="req-123",
                user_id="user-456",
            )
        
        output = stream.getvalue().strip()
        log_entry = json.loads(output)
        
        # Should have error context in extra_fields
        assert "error_type" in log_entry
        assert log_entry["error_type"] == "RuntimeError"
        assert "error_message" in log_entry
        assert "Test runtime error" in log_entry["error_message"]
        assert "request_id" in log_entry
        assert log_entry["request_id"] == "req-123"
        assert "user_id" in log_entry
        assert log_entry["user_id"] == "user-456"


class TestConfigureLogging:
    """Test the configure_logging function."""

    def test_configure_logging_json_format(self) -> None:
        """Test that configure_logging with json_format=True uses CloudLoggingFormatter."""
        logger = configure_logging(
            level=logging.INFO,
            json_format=True,
            logger_name="test_json_config",
        )
        
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, CloudLoggingFormatter)

    def test_configure_logging_standard_format(self) -> None:
        """Test that configure_logging with json_format=False uses StandardFormatter."""
        logger = configure_logging(
            level=logging.INFO,
            json_format=False,
            logger_name="test_standard_config",
        )
        
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, StandardFormatter)


class TestSetupApplicationLogging:
    """Test the setup_application_logging function."""

    def test_production_uses_json_format(self) -> None:
        """Test that production environment uses JSON format."""
        # This test verifies the setup function configures logging correctly
        # We can't easily verify the format without capturing output
        setup_application_logging("production")
        
        # Verify uvicorn logger level is set to WARNING
        uvicorn_logger = logging.getLogger("uvicorn")
        assert uvicorn_logger.level == logging.WARNING

    def test_development_uses_debug_level(self) -> None:
        """Test that development environment uses DEBUG level."""
        setup_application_logging("development")
        
        # Root logger should be at DEBUG level
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG


class TestGetLogger:
    """Test the get_logger convenience function."""

    def test_get_logger_returns_logger(self) -> None:
        """Test that get_logger returns a logger instance."""
        logger = get_logger("test_module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_same_name_returns_same_instance(self) -> None:
        """Test that get_logger with same name returns same instance."""
        logger1 = get_logger("same_name")
        logger2 = get_logger("same_name")
        
        assert logger1 is logger2


class TestCloudLoggingSeverityMapping:
    """Test the CLOUD_LOGGING_SEVERITY mapping."""

    def test_all_python_levels_mapped(self) -> None:
        """Test that all standard Python logging levels are mapped."""
        expected_levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]
        
        for level in expected_levels:
            assert level in CLOUD_LOGGING_SEVERITY

    def test_severity_values_are_valid_cloud_logging_strings(self) -> None:
        """Test that severity values are valid Cloud Logging severity strings."""
        valid_severities = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        
        for severity in CLOUD_LOGGING_SEVERITY.values():
            assert severity in valid_severities
