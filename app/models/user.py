"""
User model for authentication and tenant membership.

This module defines the User model which represents individual users
who can authenticate to access their tenant's analytics data.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel, TenantMixin


class User(BaseModel, TenantMixin, Base):
    """
    User model for authentication and authorization.
    
    Each user belongs to exactly one tenant and can authenticate
    to access that tenant's data through the dashboard.
    
    Security Notes:
        - Passwords are NEVER stored in plaintext
        - Only bcrypt hashes are stored in password_hash
        - Email verification required before full access
        - Inactive users cannot authenticate
    
    Multi-Tenancy:
        - Each user belongs to exactly ONE tenant
        - Users can only access data from their tenant (INV-3)
        - Tenant isolation enforced at authentication layer
    
    Example:
        >>> from app.core.security import hash_password
        >>> user = User(
        ...     tenant_id=1,
        ...     email="user@example.com",
        ...     password_hash=hash_password("SecurePass123!")
        ... )
        >>> user.is_verified
        False
        >>> user.mark_as_verified()
        >>> user.is_verified
        True
    """
    
    __tablename__ = "users"
    
    # ============================================================
    # COLUMNS
    # ============================================================
    
    # Core authentication fields
    email: str = Column(
        String(255), 
        unique=True, 
        nullable=False, 
        index=True,
        doc="User's email address (used for login, must be unique)"
    )
    
    password_hash: str = Column(
        String(255), 
        nullable=False,
        doc="Bcrypt hashed password (never store plaintext)"
    )
    
    # Status fields
    is_active: bool = Column(
        Boolean, 
        default=True, 
        nullable=False,
        doc="Whether user can log in (false = account disabled)"
    )
    
    # Email verification fields
    email_verified: bool = Column(
        Boolean, 
        default=False, 
        nullable=False,
        doc="Whether user has verified their email address"
    )
    
    email_verification_token: Optional[str] = Column(
        String(255), 
        nullable=True,
        doc="Token sent to user's email for verification"
    )
    
    email_verification_expires_at: Optional[datetime] = Column(
        DateTime(timezone=True), 
        nullable=True,
        doc="Expiration time for verification token (typically 24 hours)"
    )
    
    # ============================================================
    # RELATIONSHIPS
    # ============================================================
    
    tenant = relationship(
        "Tenant", 
        back_populates="users",
        doc="The tenant this user belongs to"
    )
    
    # Note: RefreshToken model not yet implemented
    # refresh_tokens = relationship(
    #     "RefreshToken",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    #     lazy="dynamic",
    #     doc="User's refresh tokens for JWT token rotation"
    # )
    
    # ============================================================
    # TABLE CONSTRAINTS
    # ============================================================
    
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_tenant_id', 'tenant_id'),
        Index('idx_users_verification_token', 'email_verification_token'),
    )
    
    # ============================================================
    # INITIALIZATION
    # ============================================================
    
    def __init__(self, **kwargs):
        """
        Initialize a User instance.
        
        Sets default values for in-memory instances (before database persist).
        SQLAlchemy handles defaults for database-loaded instances.
        
        Args:
            **kwargs: Field values (email, password_hash, tenant_id, etc.)
        """
        # Set defaults for in-memory instances
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True
        if 'email_verified' not in kwargs:
            kwargs['email_verified'] = False
        
        super().__init__(**kwargs)
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    @property
    def is_verified(self) -> bool:
        """
        Check if user's email is verified.
        
        Returns:
            True if email_verified is True, False otherwise
            
        Example:
            >>> user = User(email="test@example.com", password_hash="...")
            >>> user.is_verified
            False
            >>> user.mark_as_verified()
            >>> user.is_verified
            True
        """
        return self.email_verified
    
    @property
    def can_login(self) -> bool:
        """
        Check if user can log in.
        
        User must be both active AND verified to log in.
        
        Returns:
            True if user can log in, False otherwise
            
        Example:
            >>> user = User(email="test@example.com", password_hash="...")
            >>> user.can_login  # Not verified yet
            False
            >>> user.mark_as_verified()
            >>> user.can_login  # Verified and active
            True
            >>> user.deactivate()
            >>> user.can_login  # Verified but not active
            False
        """
        return self.is_active and self.email_verified
    
    # ============================================================
    # PUBLIC METHODS
    # ============================================================
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convert user to dictionary representation.
        
        Args:
            include_sensitive: If True, includes verification token
                             (NEVER include password_hash)
        
        Returns:
            Dictionary with user data
            
        Example:
            >>> user = User(
            ...     id=1,
            ...     email="test@example.com",
            ...     tenant_id=10,
            ...     is_active=True
            ... )
            >>> user.to_dict()
            {
                'id': 1,
                'email': 'test@example.com',
                'tenant_id': 10,
                'is_active': True,
                'email_verified': False,
                'created_at': '2024-12-03T10:30:00Z',
                'updated_at': '2024-12-03T10:30:00Z'
            }
        """
        data = {
            'id': self.id,
            'email': self.email,
            'tenant_id': self.tenant_id,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Only include sensitive fields if explicitly requested
        if include_sensitive:
            data['email_verification_token'] = self.email_verification_token
            data['email_verification_expires_at'] = (
                self.email_verification_expires_at.isoformat() 
                if self.email_verification_expires_at 
                else None
            )
        
        return data
    
    def mark_as_verified(self) -> None:
        """
        Mark user's email as verified.
        
        Clears verification token and expiration after successful verification.
        
        Example:
            >>> user = User(email="test@example.com", password_hash="...")
            >>> user.email_verification_token = "abc123"
            >>> user.mark_as_verified()
            >>> user.email_verified
            True
            >>> user.email_verification_token is None
            True
        """
        self.email_verified = True
        self.email_verification_token = None
        self.email_verification_expires_at = None
    
    def deactivate(self) -> None:
        """
        Deactivate user account.
        
        Deactivated users cannot log in but data is retained.
        
        Example:
            >>> user = User(email="test@example.com", password_hash="...")
            >>> user.is_active
            True
            >>> user.deactivate()
            >>> user.is_active
            False
        """
        self.is_active = False
    
    def activate(self) -> None:
        """
        Activate user account.
        
        Reactivates a previously deactivated account.
        
        Example:
            >>> user = User(email="test@example.com", password_hash="...")
            >>> user.deactivate()
            >>> user.is_active
            False
            >>> user.activate()
            >>> user.is_active
            True
        """
        self.is_active = True
    
    # ============================================================
    # SPECIAL METHODS
    # ============================================================
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<User(id={self.id}, email='{self.email}', "
            f"tenant_id={self.tenant_id}, active={self.is_active}, "
            f"verified={self.email_verified})>"
        )