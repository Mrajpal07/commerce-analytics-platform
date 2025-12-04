import pytest
from app.services import AuthService, TenantService
from app.core.exceptions import ValidationException, ConflictException, AuthenticationException


def test_register_user_success(db_session):
    # Create tenant first
    tenant_service = TenantService(db_session)
    tenant = tenant_service.register_tenant(
        name="Test Store",
        shopify_domain="test.myshopify.com",
        shopify_access_token="token123"
    )
    
    auth_service = AuthService(db_session)
    user = auth_service.register_user(
        email="user@example.com",
        password="SecurePass123!",
        tenant_id=tenant.id
    )
    
    assert user.id is not None
    assert user.email == "user@example.com"
    assert user.tenant_id == tenant.id
    assert user.password_hash != "SecurePass123!"
    assert user.is_active is True
    assert user.email_verified is False


def test_register_user_invalid_email(db_session):
    auth_service = AuthService(db_session)
    
    with pytest.raises(ValidationException) as exc_info:
        auth_service.register_user(
            email="invalid-email",
            password="password",
            tenant_id=1
        )
    
    assert "Invalid email format" in str(exc_info.value)


def test_register_user_duplicate_email(db_session):
    tenant_service = TenantService(db_session)
    tenant = tenant_service.register_tenant(
        name="Test",
        shopify_domain="test.myshopify.com",
        shopify_access_token="token"
    )
    
    auth_service = AuthService(db_session)
    auth_service.register_user("duplicate@example.com", "pass123", tenant.id)
    
    with pytest.raises(ConflictException) as exc_info:
        auth_service.register_user("duplicate@example.com", "pass456", tenant.id)
    
    assert "already exists" in str(exc_info.value)


def test_login_success(db_session):
    tenant_service = TenantService(db_session)
    tenant = tenant_service.register_tenant(
        name="Test",
        shopify_domain="test.myshopify.com",
        shopify_access_token="token"
    )
    
    auth_service = AuthService(db_session)
    user = auth_service.register_user("login@example.com", "MyPassword123", tenant.id)
    
    token, logged_in_user = auth_service.login("login@example.com", "MyPassword123")
    
    assert token is not None
    assert logged_in_user.id == user.id


def test_login_wrong_password(db_session):
    tenant_service = TenantService(db_session)
    tenant = tenant_service.register_tenant("Test", "test.myshopify.com", "token")
    
    auth_service = AuthService(db_session)
    auth_service.register_user("user@example.com", "CorrectPass", tenant.id)
    
    with pytest.raises(AuthenticationException) as exc_info:
        auth_service.login("user@example.com", "WrongPass")
    
    assert "Invalid email or password" in str(exc_info.value)


def test_login_user_not_found(db_session):
    auth_service = AuthService(db_session)
    
    with pytest.raises(AuthenticationException):
        auth_service.login("nonexistent@example.com", "password")