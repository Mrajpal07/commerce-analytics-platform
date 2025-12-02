"""
Unit tests for security module.
"""

import pytest
from datetime import datetime, timedelta

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    encrypt_token,
    decrypt_token,
    verify_webhook_signature,
    generate_webhook_signature,
    mask_token,
)
from app.core.exceptions import (
    TokenExpiredException,
    InvalidTokenException,
)


# ============================================================================
# PASSWORD TESTS
# ============================================================================

def test_hash_password():
    """Test password hashing."""
    password = "Pass123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert hashed.startswith("$2b$")  # bcrypt prefix
    assert len(hashed) == 60  # bcrypt hash length


def test_verify_password_success():
    """Test password verification with correct password."""
    password = "Pass123"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    """Test password verification with wrong password."""
    password = "Pass123"
    hashed = hash_password(password)
    
    assert verify_password("Wrong", hashed) is False


def test_hash_password_different_salts():
    """Test that same password produces different hashes."""
    password = "Pass123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    assert hash1 != hash2  # Different salts


# ============================================================================
# JWT ACCESS TOKEN TESTS
# ============================================================================

def test_create_access_token():
    """Test access token creation."""
    token = create_access_token(user_id=1, tenant_id=10)
    
    assert isinstance(token, str)
    assert len(token) > 50  # JWT tokens are long


def test_decode_access_token():
    """Test access token decoding."""
    token = create_access_token(user_id=1, tenant_id=10)
    payload = decode_access_token(token)
    
    assert payload["user_id"] == 1
    assert payload["tenant_id"] == 10


def test_decode_wrong_token_type():
    """Test that refresh token cannot be decoded as access token."""
    refresh_token = create_refresh_token(user_id=1)
    
    with pytest.raises(InvalidTokenException):
        decode_access_token(refresh_token)


def test_decode_invalid_token():
    """Test decoding invalid JWT token."""
    with pytest.raises(InvalidTokenException):
        decode_access_token("invalid.token.string")


# ============================================================================
# JWT REFRESH TOKEN TESTS
# ============================================================================

def test_create_refresh_token():
    """Test refresh token creation."""
    token = create_refresh_token(user_id=1)
    
    assert isinstance(token, str)
    assert len(token) > 50


def test_decode_refresh_token():
    """Test refresh token decoding."""
    token = create_refresh_token(user_id=1)
    payload = decode_refresh_token(token)
    
    assert payload["user_id"] == 1
    assert "tenant_id" not in payload  # Refresh tokens don't have tenant_id


def test_decode_refresh_token_wrong_type():
    """Test that access token cannot be decoded as refresh token."""
    access_token = create_access_token(user_id=1, tenant_id=10)
    
    with pytest.raises(InvalidTokenException):
        decode_refresh_token(access_token)


# ============================================================================
# ENCRYPTION TESTS
# ============================================================================

def test_encrypt_token():
    """Test token encryption."""
    plain = "shpat_abc123def456"
    encrypted = encrypt_token(plain)
    
    assert isinstance(encrypted, bytes)
    assert encrypted != plain.encode()


def test_decrypt_token():
    """Test token decryption."""
    plain = "shpat_abc123def456"
    encrypted = encrypt_token(plain)
    decrypted = decrypt_token(encrypted)
    
    assert decrypted == plain


def test_encrypt_decrypt_roundtrip():
    """Test encrypt/decrypt roundtrip."""
    original = "shpat_very_long_shopify_token_12345"
    encrypted = encrypt_token(original)
    decrypted = decrypt_token(encrypted)
    
    assert decrypted == original


def test_decrypt_invalid_token():
    """Test decrypting invalid data."""
    with pytest.raises(InvalidTokenException):
        decrypt_token(b"invalid encrypted data")


# ============================================================================
# WEBHOOK SIGNATURE TESTS
# ============================================================================

def test_generate_webhook_signature():
    """Test webhook signature generation."""
    payload = b'{"order_id": 123}'
    secret = "webhook_secret"
    
    signature = generate_webhook_signature(payload, secret)
    
    assert isinstance(signature, str)
    assert len(signature) > 20  # Base64-encoded SHA256


def test_verify_webhook_signature_valid():
    """Test webhook signature verification with valid signature."""
    payload = b'{"order_id": 123}'
    secret = "webhook_secret"
    
    signature = generate_webhook_signature(payload, secret)
    
    assert verify_webhook_signature(payload, signature, secret) is True


def test_verify_webhook_signature_invalid():
    """Test webhook signature verification with invalid signature."""
    payload = b'{"order_id": 123}'
    secret = "webhook_secret"
    wrong_signature = "invalid_signature"
    
    assert verify_webhook_signature(payload, wrong_signature, secret) is False


def test_verify_webhook_signature_wrong_secret():
    """Test that signature fails with wrong secret."""
    payload = b'{"order_id": 123}'
    secret = "webhook_secret"
    wrong_secret = "wrong_secret"
    
    signature = generate_webhook_signature(payload, secret)
    
    assert verify_webhook_signature(payload, signature, wrong_secret) is False


def test_verify_webhook_signature_tampered_payload():
    """Test that signature fails if payload is modified."""
    payload = b'{"order_id": 123}'
    secret = "webhook_secret"
    
    signature = generate_webhook_signature(payload, secret)
    
    tampered_payload = b'{"order_id": 456}'
    
    assert verify_webhook_signature(tampered_payload, signature, secret) is False


# ============================================================================
# UTILITY TESTS
# ============================================================================

def test_mask_token():
    """Test token masking for logs."""
    token = "shpat_abc123def456ghi789"
    masked = mask_token(token)
    
    assert "***" in masked
    assert masked.startswith("shpat_")
    assert masked.endswith("i789")
    assert "abc123" not in masked


def test_mask_short_token():
    """Test masking very short token."""
    token = "abc"
    masked = mask_token(token, visible_chars=4)
    
    assert masked == "***"