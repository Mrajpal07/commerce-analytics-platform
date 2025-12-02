"""
Idempotency Utilities

Provides functions for generating and managing idempotency keys.
Enforces INV-2: Event Idempotency.

Idempotency keys ensure that processing the same event multiple times
has the same effect as processing it once.
"""

import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

from app.core.exceptions import ValidationException


def generate_idempotency_key(
    tenant_id: int,
    entity_type: str,
    entity_id: str,
    event_type: str,
    timestamp: datetime
) -> str:
    """
    Generate a unique idempotency key for an event.
    
    Enforces INV-2: Event Idempotency.
    The key is deterministic - same inputs always produce same key.
    
    Format: {tenant_id}:{entity_type}:{entity_id}:{event_type}:{hash}
    
    Args:
        tenant_id: Tenant ID
        entity_type: Type of entity (e.g., "order", "customer")
        entity_id: External entity ID (e.g., Shopify order ID)
        event_type: Event type (e.g., "orders/create")
        timestamp: Event timestamp (from source system)
    
    Returns:
        str: Unique idempotency key
    
    Example:
        >>> from datetime import datetime
        >>> key = generate_idempotency_key(
        ...     tenant_id=1,
        ...     entity_type="order",
        ...     entity_id="12345",
        ...     event_type="orders/create",
        ...     timestamp=datetime(2024, 12, 3, 10, 30, 0)
        ... )
        >>> print(key)
        1:order:12345:orders/create:a3b5c7d9e1f2...
    
    Notes:
        - Uses SHA256 for hash generation
        - Timestamp is included to differentiate updates
        - Key is URL-safe (no spaces or special chars)
    """
    # Validate inputs
    if tenant_id <= 0:
        raise ValidationException("tenant_id must be positive")
    
    if not entity_type or not entity_type.strip():
        raise ValidationException("entity_type cannot be empty")
    
    if not entity_id or not entity_id.strip():
        raise ValidationException("entity_id cannot be empty")
    
    if not event_type or not event_type.strip():
        raise ValidationException("event_type cannot be empty")
    
    # Convert timestamp to ISO format string
    timestamp_str = timestamp.isoformat()
    
    # Create hash input
    hash_input = f"{tenant_id}:{entity_id}:{event_type}:{timestamp_str}"
    
    # Generate SHA256 hash
    hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()
    
    # Take first 16 characters of hash (sufficient uniqueness)
    hash_short = hash_digest[:16]
    
    # Construct idempotency key
    key = f"{tenant_id}:{entity_type}:{entity_id}:{event_type}:{hash_short}"
    
    return key


def generate_simple_idempotency_key(
    tenant_id: int,
    entity_type: str,
    entity_id: str,
    event_type: str
) -> str:
    """
    Generate a simpler idempotency key without timestamp.
    
    Use this when you want to deduplicate based only on entity + event type,
    ignoring when the event occurred. Useful for state-based events where
    only the latest state matters.
    
    Args:
        tenant_id: Tenant ID
        entity_type: Type of entity
        entity_id: External entity ID
        event_type: Event type
    
    Returns:
        str: Simple idempotency key
    
    Example:
        >>> key = generate_simple_idempotency_key(
        ...     tenant_id=1,
        ...     entity_type="order",
        ...     entity_id="12345",
        ...     event_type="orders/update"
        ... )
        >>> print(key)
        1:order:12345:orders/update
    """
    return f"{tenant_id}:{entity_type}:{entity_id}:{event_type}"


def parse_idempotency_key(key: str) -> Dict[str, Any]:
    """
    Parse an idempotency key into its components.
    
    Args:
        key: Idempotency key string
    
    Returns:
        Dict with components: tenant_id, entity_type, entity_id, event_type, hash
    
    Raises:
        ValidationException: If key format is invalid
    
    Example:
        >>> key = "1:order:12345:orders/create:a3b5c7d9e1f2"
        >>> components = parse_idempotency_key(key)
        >>> print(components)
        {
            'tenant_id': 1,
            'entity_type': 'order',
            'entity_id': '12345',
            'event_type': 'orders/create',
            'hash': 'a3b5c7d9e1f2'
        }
    """
    parts = key.split(":")
    
    if len(parts) < 4:
        raise ValidationException(
            f"Invalid idempotency key format: {key}",
            details={"expected_parts": "at least 4", "actual_parts": len(parts)}
        )
    
    try:
        tenant_id = int(parts[0])
    except ValueError:
        raise ValidationException(
            f"Invalid tenant_id in key: {parts[0]}",
            details={"key": key}
        )
    
    entity_type = parts[1]
    entity_id = parts[2]
    
    # Event type might contain colons (e.g., "custom:event:type")
    # Hash is the last part (if exists)
    if len(parts) > 4:
        event_type = ":".join(parts[3:-1])
        hash_value = parts[-1]
    else:
        # Simple key without hash
        event_type = parts[3]
        hash_value = None
    
    return {
        "tenant_id": tenant_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "event_type": event_type,
        "hash": hash_value
    }


def validate_idempotency_key(key: str) -> bool:
    """
    Validate that a string is a properly formatted idempotency key.
    
    Args:
        key: String to validate
    
    Returns:
        bool: True if valid, False otherwise
    
    Example:
        >>> validate_idempotency_key("1:order:12345:orders/create:abc123")
        True
        >>> validate_idempotency_key("invalid-key")
        False
    """
    try:
        parse_idempotency_key(key)
        return True
    except ValidationException:
        return False


def generate_correlation_id() -> str:
    """
    Generate a unique correlation ID for distributed tracing.
    
    Uses UUID4 format for global uniqueness.
    
    Returns:
        str: UUID4 correlation ID
    
    Example:
        >>> correlation_id = generate_correlation_id()
        >>> print(correlation_id)
        550e8400-e29b-41d4-a716-446655440000
    """
    import uuid
    return str(uuid.uuid4())


def generate_request_id(prefix: str = "req") -> str:
    """
    Generate a request ID with optional prefix.
    
    Args:
        prefix: Prefix for the request ID (default: "req")
    
    Returns:
        str: Request ID with prefix
    
    Example:
        >>> request_id = generate_request_id("api")
        >>> print(request_id)
        api-550e8400-e29b-41d4-a716-446655440000
    """
    import uuid
    return f"{prefix}-{uuid.uuid4()}"


def hash_dict(data: Dict[str, Any]) -> str:
    """
    Generate a consistent hash of a dictionary.
    
    Useful for detecting if event payload has changed.
    
    Args:
        data: Dictionary to hash
    
    Returns:
        str: SHA256 hash of dictionary
    
    Example:
        >>> payload = {"order_id": 123, "total": 99.99}
        >>> hash1 = hash_dict(payload)
        >>> hash2 = hash_dict(payload)
        >>> assert hash1 == hash2  # Deterministic
    
    Notes:
        - Keys are sorted for consistent hashing
        - Nested dictionaries are supported
        - None values are handled
    """
    import json
    
    # Convert to JSON with sorted keys for consistency
    json_str = json.dumps(data, sort_keys=True, default=str)
    
    # Generate SHA256 hash
    return hashlib.sha256(json_str.encode()).hexdigest()