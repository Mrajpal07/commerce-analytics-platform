"""
Unit tests for idempotency utilities.
"""

from datetime import datetime

import pytest

from app.core.idempotency import (
    generate_idempotency_key,
    generate_simple_idempotency_key,
    parse_idempotency_key,
    validate_idempotency_key,
    generate_correlation_id,
    generate_request_id,
    hash_dict,
)
from app.core.exceptions import ValidationException


def test_generate_idempotency_key():
    """Test idempotency key generation."""
    key = generate_idempotency_key(
        tenant_id=1,
        entity_type="order",
        entity_id="12345",
        event_type="orders/create",
        timestamp=datetime(2024, 12, 3, 10, 30, 0)
    )
    
    assert isinstance(key, str)
    assert key.startswith("1:order:12345:orders/create:")
    assert len(key.split(":")) == 5


def test_generate_idempotency_key_deterministic():
    """Test that same inputs produce same key."""
    timestamp = datetime(2024, 12, 3, 10, 30, 0)
    
    key1 = generate_idempotency_key(
        tenant_id=1,
        entity_type="order",
        entity_id="12345",
        event_type="orders/create",
        timestamp=timestamp
    )
    
    key2 = generate_idempotency_key(
        tenant_id=1,
        entity_type="order",
        entity_id="12345",
        event_type="orders/create",
        timestamp=timestamp
    )
    
    assert key1 == key2


def test_generate_idempotency_key_different_timestamps():
    """Test that different timestamps produce different keys."""
    key1 = generate_idempotency_key(
        tenant_id=1,
        entity_type="order",
        entity_id="12345",
        event_type="orders/create",
        timestamp=datetime(2024, 12, 3, 10, 30, 0)
    )
    
    key2 = generate_idempotency_key(
        tenant_id=1,
        entity_type="order",
        entity_id="12345",
        event_type="orders/create",
        timestamp=datetime(2024, 12, 3, 10, 31, 0)  # 1 minute later
    )
    
    assert key1 != key2


def test_generate_idempotency_key_validation():
    """Test validation of inputs."""
    with pytest.raises(ValidationException):
        generate_idempotency_key(
            tenant_id=0,  # Invalid
            entity_type="order",
            entity_id="12345",
            event_type="orders/create",
            timestamp=datetime.utcnow()
        )
    
    with pytest.raises(ValidationException):
        generate_idempotency_key(
            tenant_id=1,
            entity_type="",  # Empty
            entity_id="12345",
            event_type="orders/create",
            timestamp=datetime.utcnow()
        )


def test_generate_simple_idempotency_key():
    """Test simple idempotency key (no timestamp)."""
    key = generate_simple_idempotency_key(
        tenant_id=1,
        entity_type="order",
        entity_id="12345",
        event_type="orders/update"
    )
    
    assert key == "1:order:12345:orders/update"
    assert len(key.split(":")) == 4


def test_parse_idempotency_key():
    """Test parsing idempotency key."""
    key = "1:order:12345:orders/create:abc123def456"
    
    components = parse_idempotency_key(key)
    
    assert components["tenant_id"] == 1
    assert components["entity_type"] == "order"
    assert components["entity_id"] == "12345"
    assert components["event_type"] == "orders/create"
    assert components["hash"] == "abc123def456"


def test_parse_simple_idempotency_key():
    """Test parsing simple key without hash."""
    key = "1:order:12345:orders/update"
    
    components = parse_idempotency_key(key)
    
    assert components["tenant_id"] == 1
    assert components["entity_type"] == "order"
    assert components["entity_id"] == "12345"
    assert components["event_type"] == "orders/update"
    assert components["hash"] is None


def test_parse_idempotency_key_invalid():
    """Test parsing invalid key."""
    with pytest.raises(ValidationException):
        parse_idempotency_key("invalid-key")
    
    with pytest.raises(ValidationException):
        parse_idempotency_key("1:order")  # Too few parts


def test_validate_idempotency_key():
    """Test key validation."""
    valid_key = "1:order:12345:orders/create:abc123"
    invalid_key = "invalid"
    
    assert validate_idempotency_key(valid_key) is True
    assert validate_idempotency_key(invalid_key) is False


def test_generate_correlation_id():
    """Test correlation ID generation."""
    id1 = generate_correlation_id()
    id2 = generate_correlation_id()
    
    assert isinstance(id1, str)
    assert isinstance(id2, str)
    assert id1 != id2  # Should be unique
    assert len(id1) == 36  # UUID4 format


def test_generate_request_id():
    """Test request ID generation."""
    req_id = generate_request_id()
    
    assert req_id.startswith("req-")
    assert len(req_id) == 40  # "req-" + UUID


def test_generate_request_id_custom_prefix():
    """Test request ID with custom prefix."""
    api_id = generate_request_id("api")
    
    assert api_id.startswith("api-")


def test_hash_dict():
    """Test dictionary hashing."""
    data = {"order_id": 123, "total": 99.99}
    
    hash1 = hash_dict(data)
    hash2 = hash_dict(data)
    
    assert hash1 == hash2  # Deterministic
    assert isinstance(hash1, str)
    assert len(hash1) == 64  # SHA256 hex length


def test_hash_dict_order_independent():
    """Test that key order doesn't affect hash."""
    data1 = {"a": 1, "b": 2, "c": 3}
    data2 = {"c": 3, "a": 1, "b": 2}
    
    assert hash_dict(data1) == hash_dict(data2)


def test_hash_dict_nested():
    """Test hashing nested dictionaries."""
    data = {
        "order": {
            "id": 123,
            "items": [{"sku": "ABC", "qty": 2}]
        }
    }
    
    hash_value = hash_dict(data)
    
    assert isinstance(hash_value, str)
    assert len(hash_value) == 64


def test_roundtrip_generate_and_parse():
    """Test generating and parsing a key."""
    original = {
        "tenant_id": 1,
        "entity_type": "order",
        "entity_id": "12345",
        "event_type": "orders/create",
        "timestamp": datetime(2024, 12, 3, 10, 30, 0)
    }
    
    key = generate_idempotency_key(**original)
    parsed = parse_idempotency_key(key)
    
    assert parsed["tenant_id"] == original["tenant_id"]
    assert parsed["entity_type"] == original["entity_type"]
    assert parsed["entity_id"] == original["entity_id"]
    assert parsed["event_type"] == original["event_type"]
    assert parsed["hash"] is not None