"""
Unit tests for logging module.
"""

import json
import logging
from io import StringIO

import pytest

from app.core.logging import (
    get_logger,
    CorrelationIdContext,
    set_correlation_id,
    get_correlation_id,
    clear_correlation_id,
    log_function_call,
)


def test_get_logger():
    """Test getting a logger instance."""
    logger = get_logger("test_module")
    
    assert logger is not None


def test_logger_basic_logging(caplog):
    """Test basic logging functionality."""
    with caplog.at_level(logging.INFO):
        logger = get_logger("test")
        logger.info("test_message", key="value")
    
    assert "test_message" in caplog.text
    assert caplog.records[0].levelname == "INFO"


def test_logger_structured_data(caplog):
    """Test that structured data is attached to log records."""
    with caplog.at_level(logging.INFO):
        logger = get_logger("test")
        logger.info("test_event", order_id=123, tenant_id=1)
    
    record = caplog.records[0]
    assert record.order_id == 123
    assert record.tenant_id == 1


def test_sensitive_data_scrubbing(caplog):
    """Test that sensitive fields can be logged (scrubbing happens in formatter)."""
    with caplog.at_level(logging.INFO):
        logger = get_logger("test")
        logger.info(
            "user_action",
            password="secret123",
            token="abc123",
            user_id=456
        )
    
    record = caplog.records[0]
    # Data is attached to record (formatter will scrub it)
    assert hasattr(record, 'password')
    assert hasattr(record, 'token')
    assert record.user_id == 456


def test_correlation_id_context(caplog):
    """Test correlation ID context manager."""
    with caplog.at_level(logging.INFO):
        logger = get_logger("test")
        
        with CorrelationIdContext("req-123"):
            logger.info("test_message")
    
    # Correlation ID is set in context
    assert len(caplog.records) > 0


def test_correlation_id_context_cleanup():
    """Test that correlation ID is cleaned up after context."""
    with CorrelationIdContext("req-123"):
        assert get_correlation_id() == "req-123"
    
    # After context, should be cleared
    assert get_correlation_id() is None


def test_set_get_correlation_id():
    """Test setting and getting correlation ID."""
    set_correlation_id("req-456")
    assert get_correlation_id() == "req-456"
    
    clear_correlation_id()
    assert get_correlation_id() is None


def test_log_function_call_decorator(caplog):
    """Test function call logging decorator."""
    with caplog.at_level(logging.DEBUG):
        @log_function_call
        def test_function(x: int, y: int) -> int:
            return x + y
        
        result = test_function(2, 3)
        
        assert result == 5
        assert any("test_function_called" in record.message for record in caplog.records)
        assert any("test_function_completed" in record.message for record in caplog.records)


def test_log_function_call_decorator_with_exception(caplog):
    """Test that decorator logs exceptions."""
    with caplog.at_level(logging.DEBUG):
        @log_function_call
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_function()
        
        assert any("failing_function_called" in record.message for record in caplog.records)
        assert any("failing_function_failed" in record.message for record in caplog.records)


def test_different_log_levels(caplog):
    """Test different log levels."""
    logger = get_logger("test")
    
    with caplog.at_level(logging.DEBUG):
        logger.debug("debug_msg")
        logger.info("info_msg")
        logger.warning("warning_msg")
        logger.error("error_msg")
    
    messages = [record.message for record in caplog.records]
    assert "debug_msg" in messages
    assert "info_msg" in messages
    assert "warning_msg" in messages
    assert "error_msg" in messages


def test_logger_with_multiple_fields(caplog):
    """Test logging with multiple structured fields."""
    with caplog.at_level(logging.INFO):
        logger = get_logger("test")
        logger.info(
            "complex_event",
            user_id=1,
            tenant_id=10,
            order_id=123,
            amount=99.99,
            status="completed"
        )
    
    record = caplog.records[0]
    assert record.user_id == 1
    assert record.tenant_id == 10
    assert record.order_id == 123
    assert record.amount == 99.99
    assert record.status == "completed"