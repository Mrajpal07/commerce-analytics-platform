from typing import Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User
from app.repositories import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import (
    ValidationException,
    AuthenticationException,
    NotFoundException,
    ConflictException
)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def register_user(
        self,
        email: str,
        password: str,
        tenant_id: int
    ) -> User:
        """Register new user with email verification."""
        # Validate email
        if not email or '@' not in email:
            raise ValidationException(
                "Invalid email format",
                details={"email": email}
            )
        
        # Check if user exists
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ConflictException(
                message=f"User with email '{email}' already exists",
                error_code="USER_ALREADY_EXISTS",
                details={"email": email}
            )
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        user = User(
            tenant_id=tenant_id,
            email=email,
            password_hash=password_hash,
            is_active=True,
            email_verified=False
        )
        
        created_user = self.user_repo.create(user)
        self.db.commit()
        
        return created_user
    
    def login(self, email: str, password: str) -> Tuple[str, User]:
        """Authenticate user and return access token."""
        user = self.user_repo.get_by_email(email)
        
        if not user:
            raise AuthenticationException(
                "Invalid email or password",
                details={"email": email}
            )
        
        if not verify_password(password, user.password_hash):
            raise AuthenticationException(
                "Invalid email or password",
                details={"email": email}
            )
        
        if not user.is_active:
            raise AuthenticationException(
                "User account is deactivated",
                details={"user_id": user.id}
            )
        
        # Generate JWT token
        access_token = create_access_token(
            user_id=user.id,
            tenant_id=user.tenant_id
        )
        
        return access_token, user
    
    def verify_email(self, token: str) -> User:
        """Verify user email with token."""
        user = self.user_repo.get_by_verification_token(token)
        
        if not user:
            raise NotFoundException(
                resource_type="Verification token",
                identifier=token
            )
        
        # Check token expiration
        if user.email_verification_expires_at and user.email_verification_expires_at < datetime.utcnow():
            raise ValidationException(
                "Verification token expired",
                details={"token": token}
            )
        
        user.mark_as_verified()
        self.user_repo.update(user)
        self.db.commit()
        
        return user
    
    def get_user(self, user_id: int) -> User:
        """Get user by ID."""
        user = self.user_repo.get(user_id)
        if not user:
            raise NotFoundException(resource_type="User", identifier=user_id)
        return user