"""
Core Exception Classes

Defines the exception hierarchy for the application.
All exceptions inherit from AppException and provide structured error information.

Exception hierarchy maps to HTTP status codes for API responses.
"""

from typing import Optional, Dict, Any


class AppException(Exception):
    """
    Base exception for all application errors.
    
    Provides structured error information that can be serialized to JSON
    for API responses or logged for debugging.
    
    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code (e.g., "TENANT_NOT_FOUND")
        status_code: HTTP status code for API responses
        details: Additional context (e.g., {"tenant_id": 123})
        retry_after: Optional retry delay in seconds (for rate limits)
    """
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.retry_after = retry_after
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON serialization.
        
        Returns:
            Dict suitable for API error response
        """
        result = {
            "error": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
        }
        
        if self.details:
            result["details"] = self.details
        
        if self.retry_after is not None:
            result["retry_after"] = self.retry_after
        
        return result
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(code={self.error_code}, message='{self.message}')>"


# ============================================================================
# VALIDATION EXCEPTIONS (400)
# ============================================================================

class ValidationException(AppException):
    """Base class for validation errors (HTTP 400)."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class InvalidInputException(ValidationException):
    """Invalid input data provided."""
    
    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Invalid input for field '{field}': {reason}",
            details={"field": field, "reason": reason}
        )


class SchemaValidationException(ValidationException):
    """Data does not match expected schema."""
    
    def __init__(self, errors: Dict[str, Any]):
        super().__init__(
            message="Schema validation failed",
            details={"validation_errors": errors}
        )


# ============================================================================
# AUTHENTICATION EXCEPTIONS (401)
# ============================================================================

class AuthenticationException(AppException):
    """Base class for authentication errors (HTTP 401)."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class InvalidCredentialsException(AuthenticationException):
    """Invalid username/password."""
    
    def __init__(self):
        super().__init__(
            message="Invalid credentials provided"
        )


class TokenExpiredException(AuthenticationException):
    """JWT token has expired."""
    
    def __init__(self):
        super().__init__(
            message="Authentication token has expired"
        )


class InvalidTokenException(AuthenticationException):
    """JWT token is invalid or malformed."""
    
    def __init__(self, reason: Optional[str] = None):
        details = {"reason": reason} if reason else None
        super().__init__(
            message="Invalid authentication token",
            details=details
        )


# ============================================================================
# AUTHORIZATION EXCEPTIONS (403)
# ============================================================================

class AuthorizationException(AppException):
    """Base class for authorization errors (HTTP 403)."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details
        )


class TenantIsolationViolationException(AuthorizationException):
    """
    Attempted to access data from another tenant (INV-3 violation).
    
    This is a CRITICAL security exception.
    """
    
    def __init__(self, requested_tenant_id: int, actual_tenant_id: int):
        super().__init__(
            message="Access denied: Tenant isolation violation",
            details={
                "requested_tenant_id": requested_tenant_id,
                "actual_tenant_id": actual_tenant_id
            }
        )


class InsufficientPermissionsException(AuthorizationException):
    """User lacks required permissions."""
    
    def __init__(self, required_permission: str):
        super().__init__(
            message=f"Insufficient permissions: '{required_permission}' required",
            details={"required_permission": required_permission}
        )


# ============================================================================
# NOT FOUND EXCEPTIONS (404)
# ============================================================================

class NotFoundException(AppException):
    """Base class for resource not found errors (HTTP 404)."""
    
    def __init__(self, resource_type: str, identifier: Any):
        super().__init__(
            message=f"{resource_type} not found",
            error_code=f"{resource_type.upper()}_NOT_FOUND",
            status_code=404,
            details={"resource_type": resource_type, "identifier": str(identifier)}
        )


class TenantNotFoundException(NotFoundException):
    """Tenant does not exist."""
    
    def __init__(self, tenant_id: int):
        super().__init__(resource_type="Tenant", identifier=tenant_id)


class OrderNotFoundException(NotFoundException):
    """Order does not exist."""
    
    def __init__(self, order_id: int):
        super().__init__(resource_type="Order", identifier=order_id)


class EventNotFoundException(NotFoundException):
    """Event does not exist."""
    
    def __init__(self, event_id: int):
        super().__init__(resource_type="Event", identifier=event_id)


class CustomerNotFoundException(NotFoundException):
    """Customer does not exist."""
    
    def __init__(self, customer_id: int):
        super().__init__(resource_type="Customer", identifier=customer_id)


# ============================================================================
# CONFLICT EXCEPTIONS (409)
# ============================================================================

class ConflictException(AppException):
    """Base class for conflict errors (HTTP 409)."""
    
    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=409,
            details=details
        )


class IdempotencyViolationException(ConflictException):
    """
    Duplicate event with same idempotency key (INV-2 violation).
    
    This is expected behavior - return success to client.
    """
    
    def __init__(self, idempotency_key: str):
        super().__init__(
            message="Event already processed",
            error_code="IDEMPOTENCY_VIOLATION",
            details={"idempotency_key": idempotency_key}
        )


class DuplicateOrderException(ConflictException):
    """
    Order already exists for this tenant (INV-1 violation).
    """
    
    def __init__(self, tenant_id: int, shopify_order_id: int):
        super().__init__(
            message="Order already exists",
            error_code="DUPLICATE_ORDER",
            details={
                "tenant_id": tenant_id,
                "shopify_order_id": shopify_order_id
            }
        )


class EventOrderingViolationException(ConflictException):
    """
    Event arrived out of order (INV-4 violation).
    
    Requires fetching missing events from source.
    """
    
    def __init__(self, entity_type: str, entity_id: str, expected_seq: int, actual_seq: int):
        super().__init__(
            message="Event ordering violation detected",
            error_code="EVENT_ORDERING_VIOLATION",
            details={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "expected_sequence": expected_seq,
                "actual_sequence": actual_seq
            }
        )


# ============================================================================
# EXTERNAL API EXCEPTIONS (502/503)
# ============================================================================

class ExternalAPIException(AppException):
    """Base class for external API errors."""
    
    def __init__(
        self,
        service: str,
        message: str,
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None
    ):
        super().__init__(
            message=f"{service} API error: {message}",
            error_code=f"{service.upper()}_API_ERROR",
            status_code=status_code,
            details=details,
            retry_after=retry_after
        )


class ShopifyAPIException(ExternalAPIException):
    """Shopify API returned an error."""
    
    def __init__(self, status_code: int, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            service="Shopify",
            message=message,
            status_code=502,
            details={**(details or {}), "shopify_status_code": status_code}
        )


class ShopifyRateLimitException(ExternalAPIException):
    """Shopify API rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            service="Shopify",
            message="Rate limit exceeded",
            status_code=503,
            retry_after=retry_after
        )


# ============================================================================
# INTERNAL EXCEPTIONS (500)
# ============================================================================

class InternalException(AppException):
    """Base class for internal server errors (HTTP 500)."""
    
    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=500,
            details=details
        )


class DatabaseException(InternalException):
    """Database operation failed."""
    
    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Database {operation} failed: {reason}",
            error_code="DATABASE_ERROR",
            details={"operation": operation, "reason": reason}
        )


class TaskExecutionException(InternalException):
    """Celery task execution failed."""
    
    def __init__(self, task_name: str, reason: str):
        super().__init__(
            message=f"Task '{task_name}' execution failed: {reason}",
            error_code="TASK_EXECUTION_ERROR",
            details={"task_name": task_name, "reason": reason}
        )


class ConfigurationException(InternalException):
    """Application configuration error."""
    
    def __init__(self, config_key: str, reason: str):
        super().__init__(
            message=f"Configuration error for '{config_key}': {reason}",
            error_code="CONFIGURATION_ERROR",
            details={"config_key": config_key, "reason": reason}
        )