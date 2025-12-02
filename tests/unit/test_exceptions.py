"""
Unit tests for core exceptions.
"""

import pytest
from app.core.exceptions import (
    AppException,
    ValidationException,
    InvalidInputException,
    TenantNotFoundException,
    IdempotencyViolationException,
    TenantIsolationViolationException,
    ShopifyRateLimitException,
    DatabaseException,
)


def test_app_exception_base():
    """Test base AppException."""
    exc = AppException(
        message="Test error",
        error_code="TEST_ERROR",
        status_code=500,
        details={"key": "value"}
    )
    
    assert exc.message == "Test error"
    assert exc.error_code == "TEST_ERROR"
    assert exc.status_code == 500
    assert exc.details == {"key": "value"}
    assert exc.retry_after is None


def test_app_exception_to_dict():
    """Test exception serialization."""
    exc = AppException(
        message="Test error",
        error_code="TEST_ERROR",
        status_code=400
    )
    
    result = exc.to_dict()
    
    assert result["error"] == "TEST_ERROR"
    assert result["message"] == "Test error"
    assert result["status_code"] == 400


def test_validation_exception():
    """Test validation exception."""
    exc = ValidationException(
        message="Invalid data",
        details={"field": "email"}
    )
    
    assert exc.status_code == 400
    assert exc.error_code == "VALIDATION_ERROR"
    assert exc.details["field"] == "email"


def test_invalid_input_exception():
    """Test invalid input exception."""
    exc = InvalidInputException(
        field="age",
        reason="must be positive"
    )
    
    assert exc.status_code == 400
    assert "age" in exc.message
    assert "must be positive" in exc.message


def test_tenant_not_found_exception():
    """Test tenant not found exception."""
    exc = TenantNotFoundException(tenant_id=123)
    
    assert exc.status_code == 404
    assert "TENANT_NOT_FOUND" in exc.error_code
    assert exc.details["identifier"] == "123"


def test_idempotency_violation_exception():
    """Test idempotency violation exception (INV-2)."""
    exc = IdempotencyViolationException(idempotency_key="key123")
    
    assert exc.status_code == 409
    assert exc.error_code == "IDEMPOTENCY_VIOLATION"
    assert exc.details["idempotency_key"] == "key123"


def test_tenant_isolation_violation_exception():
    """Test tenant isolation violation (INV-3)."""
    exc = TenantIsolationViolationException(
        requested_tenant_id=1,
        actual_tenant_id=2
    )
    
    assert exc.status_code == 403
    assert exc.details["requested_tenant_id"] == 1
    assert exc.details["actual_tenant_id"] == 2


def test_shopify_rate_limit_exception():
    """Test Shopify rate limit exception with retry."""
    exc = ShopifyRateLimitException(retry_after=60)
    
    assert exc.status_code == 503
    assert exc.retry_after == 60
    assert "Shopify" in exc.message


def test_database_exception():
    """Test database exception."""
    exc = DatabaseException(
        operation="INSERT",
        reason="connection timeout"
    )
    
    assert exc.status_code == 500
    assert exc.error_code == "DATABASE_ERROR"
    assert exc.details["operation"] == "INSERT"


def test_exception_with_retry_after_in_dict():
    """Test that retry_after appears in serialized output."""
    exc = ShopifyRateLimitException(retry_after=120)
    result = exc.to_dict()
    
    assert result["retry_after"] == 120


def test_exception_repr():
    """Test exception string representation."""
    exc = ValidationException(message="Test")
    repr_str = repr(exc)
    
    assert "ValidationException" in repr_str
    assert "VALIDATION_ERROR" in repr_str