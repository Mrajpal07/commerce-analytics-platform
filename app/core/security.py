"""
Core Security Module

Provides cryptographic utilities for:
- JWT token generation and validation
- Password hashing and verification
- Sensitive data encryption (Shopify tokens)
- Webhook signature verification (HMAC)

Enforces:
- INV-11: Credential Confidentiality
- INV-12: Webhook Authenticity
"""

import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from jose import JWTError, jwt
import bcrypt
from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings
from app.core.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    ConfigurationException,
)

# Get configuration
config = get_settings()

# ============================================================================
# PASSWORD HASHING
# ============================================================================


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        password: Plain-text password

    Returns:
        str: Hashed password

    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> print(hashed)
        $2b$12$...
    """
    # Convert password to bytes and hash with bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a hashed password.

    Args:
        plain_password: Plain-text password to verify
        hashed_password: Previously hashed password

    Returns:
        bool: True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> verify_password("SecurePass123!", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    # Convert both to bytes for bcrypt comparison
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ============================================================================
# JWT TOKEN OPERATIONS
# ============================================================================

def create_access_token(user_id: int, tenant_id: int) -> str:
    """
    Create a JWT access token for authentication.
    
    Access tokens are short-lived (15 minutes by default) and contain
    both user_id and tenant_id for proper isolation.
    
    Args:
        user_id: User ID
        tenant_id: Tenant ID (for isolation)
    
    Returns:
        str: Encoded JWT token
    
    Example:
        >>> token = create_access_token(user_id=1, tenant_id=10)
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    now = datetime.utcnow()
    expires_delta = timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(user_id),           # Subject (user ID)
        "tenant_id": tenant_id,        # Tenant isolation
        "type": "access",              # Token type
        "exp": now + expires_delta,    # Expiration
        "iat": now,                    # Issued at
    }
    
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """
    Create a JWT refresh token for obtaining new access tokens.
    
    Refresh tokens are long-lived (7 days by default) and only contain
    user_id. They're used to generate new access tokens.
    
    Args:
        user_id: User ID
    
    Returns:
        str: Encoded JWT token
    
    Example:
        >>> token = create_refresh_token(user_id=1)
    """
    now = datetime.utcnow()
    expires_delta = timedelta(days=config.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = {
        "sub": str(user_id),           # Subject (user ID)
        "type": "refresh",             # Token type
        "exp": now + expires_delta,    # Expiration
        "iat": now,                    # Issued at
    }
    
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token string
    
    Returns:
        Dict containing user_id and tenant_id
    
    Raises:
        TokenExpiredException: If token has expired
        InvalidTokenException: If token is invalid or wrong type
    
    Example:
        >>> token = create_access_token(user_id=1, tenant_id=10)
        >>> payload = decode_access_token(token)
        >>> print(payload)
        {"user_id": 1, "tenant_id": 10}
    """
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )
        
        # Verify token type
        if payload.get("type") != "access":
            raise InvalidTokenException(reason = "Token is not an access token")
        
        # Extract and validate required fields
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        
        if user_id is None or tenant_id is None:
            raise InvalidTokenException("Token missing required fields")
        
        return {
            "user_id": int(user_id),
            "tenant_id": int(tenant_id)
        }
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError as e:
        raise InvalidTokenException(reason=str(e))


def decode_refresh_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT refresh token.
    
    Args:
        token: JWT token string
    
    Returns:
        Dict containing user_id
    
    Raises:
        TokenExpiredException: If token has expired
        InvalidTokenException: If token is invalid or wrong type
    
    Example:
        >>> token = create_refresh_token(user_id=1)
        >>> payload = decode_refresh_token(token)
        >>> print(payload)
        {"user_id": 1}
    """
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )
        
        # Verify token type
        if payload.get("type") != "refresh":
            raise InvalidTokenException(reason="Token is not a refresh token")
        
        # Extract user_id
        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidTokenException("Token missing user ID")
        
        return {"user_id": int(user_id)}
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError as e:
        raise InvalidTokenException(reason=str(e))


# ============================================================================
# ENCRYPTION (for Shopify tokens - INV-11)
# ============================================================================

def _get_fernet() -> Fernet:
    """
    Get Fernet cipher instance.
    
    Raises:
        ConfigurationException: If encryption key is invalid
    """
    try:
        return Fernet(config.FERNET_ENCRYPTION_KEY.encode())
    except Exception as e:
        raise ConfigurationException(
            config_key="FERNET_ENCRYPTION_KEY",
            reason=f"Invalid encryption key: {str(e)}"
        )


def encrypt_token(plain_token: str) -> bytes:
    """
    Encrypt a sensitive token (e.g., Shopify access token).
    
    Uses Fernet symmetric encryption (AES-128 in CBC mode).
    Enforces INV-11: Credential Confidentiality.
    
    Args:
        plain_token: Plain-text token
    
    Returns:
        bytes: Encrypted token (store this in database)
    
    Example:
        >>> encrypted = encrypt_token("shpat_abc123...")
        >>> # Store encrypted bytes in database BYTEA column
    """
    fernet = _get_fernet()
    return fernet.encrypt(plain_token.encode())


def decrypt_token(encrypted_token: bytes) -> str:
    """
    Decrypt an encrypted token.
    
    Args:
        encrypted_token: Encrypted token bytes (from database)
    
    Returns:
        str: Plain-text token
    
    Raises:
        InvalidTokenException: If decryption fails
    
    Example:
        >>> encrypted = encrypt_token("shpat_abc123...")
        >>> plain = decrypt_token(encrypted)
        >>> print(plain)
        shpat_abc123...
    """
    fernet = _get_fernet()
    try:
        return fernet.decrypt(encrypted_token).decode()
    except InvalidToken:
        raise InvalidTokenException("Failed to decrypt token")


# ============================================================================
# WEBHOOK SIGNATURE VERIFICATION (INV-12)
# ============================================================================

def generate_webhook_signature(payload: bytes, secret: str) -> str:
    """
    Generate HMAC-SHA256 signature for webhook payload.
    
    This is used for testing/verification purposes.
    
    Args:
        payload: Raw webhook payload bytes
        secret: Webhook secret
    
    Returns:
        str: Base64-encoded HMAC signature
    
    Example:
        >>> payload = b'{"order_id": 123}'
        >>> signature = generate_webhook_signature(payload, "secret")
    """
    signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).digest()
    
    # Return base64-encoded signature
    import base64
    return base64.b64encode(signature).decode()


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify Shopify webhook signature.
    
    Enforces INV-12: Webhook Authenticity.
    Prevents malicious webhook injection.
    
    Args:
        payload: Raw webhook payload bytes (request.body)
        signature: X-Shopify-Hmac-SHA256 header value
        secret: Tenant's webhook secret
    
    Returns:
        bool: True if signature is valid, False otherwise
    
    Example:
        >>> payload = await request.body()
        >>> signature = request.headers.get("X-Shopify-Hmac-SHA256")
        >>> secret = tenant.webhook_secret
        >>> if not verify_webhook_signature(payload, signature, secret):
        ...     raise InvalidTokenException("Invalid webhook signature")
    
    Security Notes:
        - Uses constant-time comparison to prevent timing attacks
        - Signature is HMAC-SHA256 of raw payload
        - Must use raw bytes, not parsed JSON
    """
    expected_signature = generate_webhook_signature(payload, secret)
    
    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, signature)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def mask_token(token: str, visible_chars: int = 4) -> str:
    """
    Mask a token for logging (show only last N characters).
    
    Args:
        token: Token to mask
        visible_chars: Number of characters to show at end
    
    Returns:
        str: Masked token
    
    Example:
        >>> mask_token("shpat_abc123def456ghi789")
        shpat_***i789
    """
    if len(token) <= visible_chars:
        return "*" * len(token)
    
    return token[:6] + "***" + token[-visible_chars:]