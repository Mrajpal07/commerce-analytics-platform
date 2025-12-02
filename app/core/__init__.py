
"""
Core utilities package.

Exports commonly used core functionality.
"""

"""
Core utilities package.

Exports commonly used core functionality.
"""


from app.core.logging import (
    get_logger,
    CorrelationIdContext,
    set_correlation_id,
    get_correlation_id,
    clear_correlation_id,
    log_function_call,
)


from app.core.security import (
    # Password operations
    hash_password,
    verify_password,
    
    # JWT operations
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    
    # Encryption
    encrypt_token,
    decrypt_token,
    
    # Webhook verification
    verify_webhook_signature,
    generate_webhook_signature,
    
    # Utilities
    mask_token,
)



"""
Core utilities package.

Exports commonly used core functionality.
"""
from app.core.exceptions import (
    # Base
    AppException,
    
    # Validation (400)
    ValidationException,
    InvalidInputException,
    SchemaValidationException,
    
    # Authentication (401)
    AuthenticationException,
    InvalidCredentialsException,
    TokenExpiredException,
    InvalidTokenException,
    
    # Authorization (403)
    AuthorizationException,
    TenantIsolationViolationException,
    InsufficientPermissionsException,
    
    # Not Found (404)
    NotFoundException,
    TenantNotFoundException,
    OrderNotFoundException,
    EventNotFoundException,
    CustomerNotFoundException,
    
    # Conflict (409)
    ConflictException,
    IdempotencyViolationException,
    DuplicateOrderException,
    EventOrderingViolationException,
    
    # External API (502/503)
    ExternalAPIException,
    ShopifyAPIException,
    ShopifyRateLimitException,
    
    # Internal (500)
    InternalException,
    DatabaseException,
    TaskExecutionException,
    ConfigurationException,
)


# Import constants (make them available but don't export all)
from app.core import constants



from app.core.idempotency import (
    generate_idempotency_key,
    generate_simple_idempotency_key,
    parse_idempotency_key,
    validate_idempotency_key,
    generate_correlation_id,
    generate_request_id,
    hash_dict,
)

__all__ = [
    # Base
    "AppException",
    
    # Validation
    "ValidationException",
    "InvalidInputException",
    "SchemaValidationException",
    
    # Authentication
    "AuthenticationException",
    "InvalidCredentialsException",
    "TokenExpiredException",
    "InvalidTokenException",
    
    # Authorization
    "AuthorizationException",
    "TenantIsolationViolationException",
    "InsufficientPermissionsException",
    
    # Not Found
    "NotFoundException",
    "TenantNotFoundException",
    "OrderNotFoundException",
    "EventNotFoundException",
    "CustomerNotFoundException",
    
    # Conflict
    "ConflictException",
    "IdempotencyViolationException",
    "DuplicateOrderException",
    "EventOrderingViolationException",
    
    # External API
    "ExternalAPIException",
    "ShopifyAPIException",
    "ShopifyRateLimitException",
    
    # Internal
    "InternalException",
    "DatabaseException",
    "TaskExecutionException",
    "ConfigurationException",

    # Logging
    "get_logger",
    "CorrelationIdContext",
    "set_correlation_id",
    "get_correlation_id",
    "clear_correlation_id",
    "log_function_call",




    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_access_token",
    "decode_refresh_token",
    "encrypt_token",
    "decrypt_token",
    "verify_webhook_signature",
    "generate_webhook_signature",
    "mask_token",

    # Constants module (import as: from app.core import constants)
    "constants",

    # Idempotency
    "generate_idempotency_key",
    "generate_simple_idempotency_key",
    "parse_idempotency_key",
    "validate_idempotency_key",
    "generate_correlation_id",
    "generate_request_id",
    "hash_dict",
]
