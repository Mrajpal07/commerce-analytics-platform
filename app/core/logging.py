"""
Core Logging Module

Provides structured JSON logging with:
- Correlation ID tracking for distributed tracing
- Automatic secret scrubbing for security
- Consistent log formatting across the application
- Integration with observability tools

Usage:
    from app.core.logging import get_logger
    
    logger = get_logger(__name__)
    logger.info("order_created", order_id=123, tenant_id=1)
"""

import logging
import sys
import json
from typing import Any, Dict, Optional
from datetime import datetime
from contextvars import ContextVar

from pythonjsonlogger import jsonlogger

from app.config import get_settings

# Get configuration
config = get_settings()

# Context variable for correlation ID (thread-safe)
correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)

# Sensitive field names to scrub from logs
SENSITIVE_FIELDS = {
    "password",
    "token",
    "secret",
    "api_key",
    "access_token",
    "refresh_token",
    "shopify_access_token",
    "webhook_secret",
    "jwt_secret",
    "encryption_key",
    "fernet_key",
    "private_key",
    "client_secret",
}


# ============================================================================
# CUSTOM JSON FORMATTER
# ============================================================================

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds:
    - Correlation ID from context
    - Timestamp in ISO format
    - Automatic secret scrubbing
    """
    
    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any]
    ) -> None:
        """
        Add custom fields to log record.
        
        Args:
            log_record: Dictionary that will be logged
            record: LogRecord instance
            message_dict: Dictionary of message fields
        """
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        # Add log level
        log_record["level"] = record.levelname
        
        # Add logger name
        log_record["logger"] = record.name
        
        # Add correlation ID if present
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_record["correlation_id"] = correlation_id
        
        # Add environment
        log_record["environment"] = config.APP_ENV
        
        # Scrub sensitive data
        self._scrub_sensitive_data(log_record)
    
    def _scrub_sensitive_data(self, log_record: Dict[str, Any]) -> None:
        """
        Recursively scrub sensitive fields from log record.
        
        Args:
            log_record: Log record dictionary to scrub
        """
        for key, value in list(log_record.items()):
            # Check if field name is sensitive
            if key.lower() in SENSITIVE_FIELDS:
                log_record[key] = "***REDACTED***"
            
            # Recursively scrub nested dictionaries
            elif isinstance(value, dict):
                self._scrub_sensitive_data(value)
            
            # Scrub lists
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._scrub_sensitive_data(item)


# ============================================================================
# LOGGER SETUP
# ============================================================================

def setup_logging() -> None:
    """
    Configure application-wide logging.
    
    Sets up:
    - JSON formatter for structured logging
    - Log level from configuration
    - Handler for stdout
    
    Called automatically when module is imported.
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Set log level from config
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create stdout handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Set JSON formatter
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(logger)s %(message)s"
    )
    handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(handler)
    
    # Suppress overly verbose third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.WARNING)


class StructuredLogger:
    """
    Wrapper around standard logger that accepts structured kwargs.
    
    Allows: logger.info("message", key=value)
    Instead of: logger.info("message", extra={"key": value})
    """
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
    
    def _log(self, level: int, msg: str, **kwargs) -> None:
        """
        Log with structured data.
        
        Args:
            level: Log level
            msg: Log message
            **kwargs: Structured data to include in log
        """
        self._logger.log(level, msg, extra=kwargs)
    
    def debug(self, msg: str, **kwargs) -> None:
        """Log debug message with structured data."""
        self._log(logging.DEBUG, msg, **kwargs)
    
    def info(self, msg: str, **kwargs) -> None:
        """Log info message with structured data."""
        self._log(logging.INFO, msg, **kwargs)
    
    def warning(self, msg: str, **kwargs) -> None:
        """Log warning message with structured data."""
        self._log(logging.WARNING, msg, **kwargs)
    
    def error(self, msg: str, **kwargs) -> None:
        """Log error message with structured data."""
        self._log(logging.ERROR, msg, **kwargs)
    
    def critical(self, msg: str, **kwargs) -> None:
        """Log critical message with structured data."""
        self._log(logging.CRITICAL, msg, **kwargs)
    
    def exception(self, msg: str, **kwargs) -> None:
        """Log exception with structured data."""
        self._logger.exception(msg, extra=kwargs)


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance for a module.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        StructuredLogger: Configured logger instance
    
    Example:
        >>> from app.core.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("user_login", user_id=123)
    """
    standard_logger = logging.getLogger(name)
    return StructuredLogger(standard_logger)


# ============================================================================
# CORRELATION ID CONTEXT
# ============================================================================

class CorrelationIdContext:
    """
    Context manager for setting correlation ID.
    
    Usage:
        with CorrelationIdContext("req-abc123"):
            logger.info("processing_request")
            # correlation_id automatically added to logs
    """
    
    def __init__(self, correlation_id: str):
        """
        Initialize context with correlation ID.
        
        Args:
            correlation_id: Unique ID for tracking related operations
        """
        self.correlation_id = correlation_id
        self.token = None
    
    def __enter__(self) -> str:
        """Set correlation ID in context."""
        self.token = correlation_id_var.set(self.correlation_id)
        return self.correlation_id
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Clear correlation ID from context."""
        if self.token:
            correlation_id_var.reset(self.token)


def set_correlation_id(correlation_id: str) -> None:
    """
    Set correlation ID for current context.
    
    Args:
        correlation_id: Unique ID for tracking
    
    Example:
        >>> set_correlation_id("req-123")
        >>> logger.info("test")  # Will include correlation_id
    """
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """
    Get current correlation ID from context.
    
    Returns:
        Optional[str]: Correlation ID or None
    """
    return correlation_id_var.get()


def clear_correlation_id() -> None:
    """Clear correlation ID from context."""
    correlation_id_var.set(None)


# ============================================================================
# INITIALIZATION
# ============================================================================

# Setup logging when module is imported
setup_logging()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def log_function_call(func):
    """
    Decorator to log function entry and exit.
    
    Usage:
        @log_function_call
        def process_order(order_id: int):
            ...
    
    Args:
        func: Function to decorate
    
    Returns:
        Wrapped function
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        func_name = func.__qualname__
        
        # Log entry
        logger.debug(
            f"{func_name}_called",
            function=func_name,
            args_count=len(args),
            kwargs_keys=list(kwargs.keys())
        )
        
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # Log success
            duration_ms = (time.time() - start_time) * 1000
            logger.debug(
                f"{func_name}_completed",
                function=func_name,
                duration_ms=round(duration_ms, 2)
            )
            
            return result
            
        except Exception as e:
            # Log failure
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"{func_name}_failed",
                function=func_name,
                duration_ms=round(duration_ms, 2),
                error_type=type(e).__name__,
                error_message=str(e)
            )
            raise
    
    return wrapper