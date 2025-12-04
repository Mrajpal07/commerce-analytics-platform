import pytest
from app.services import TenantService
from app.core.exceptions import ValidationException, ConflictException, NotFoundException


def test_register_tenant_success(db_session):
    service = TenantService(db_session)
    
    tenant = service.register_tenant(
        name="Test Store",
        shopify_domain="test-store.myshopify.com",
        shopify_access_token="shpat_test_token_123"
    )
    
    assert tenant.id is not None
    assert tenant.name == "Test Store"
    assert tenant.shopify_domain == "test-store.myshopify.com"
    assert tenant.status == "active"
    assert tenant.shopify_access_token != "shpat_test_token_123"  # Should be encrypted


def test_register_tenant_invalid_domain(db_session):
    service = TenantService(db_session)
    
    with pytest.raises(ValidationException) as exc_info:
        service.register_tenant(
            name="Invalid",
            shopify_domain="invalid-domain.com",
            shopify_access_token="token"
        )
    
    assert "Invalid Shopify domain" in str(exc_info.value)


def test_register_tenant_duplicate_domain(db_session):
    service = TenantService(db_session)
    
    service.register_tenant(
        name="First",
        shopify_domain="duplicate.myshopify.com",
        shopify_access_token="token1"
    )
    
    with pytest.raises(ConflictException) as exc_info:
        service.register_tenant(
            name="Second",
            shopify_domain="duplicate.myshopify.com",
            shopify_access_token="token2"
        )
    
    assert "already exists" in str(exc_info.value)


def test_get_tenant_success(db_session):
    service = TenantService(db_session)
    
    created = service.register_tenant(
        name="Test",
        shopify_domain="get-test.myshopify.com",
        shopify_access_token="token"
    )
    
    fetched = service.get_tenant(created.id)
    assert fetched.id == created.id
    assert fetched.shopify_domain == "get-test.myshopify.com"


def test_get_tenant_not_found(db_session):
    service = TenantService(db_session)
    
    with pytest.raises(NotFoundException):
        service.get_tenant(99999)


def test_get_decrypted_access_token(db_session):
    service = TenantService(db_session)
    
    original_token = "shpat_original_token_123"
    tenant = service.register_tenant(
        name="Decrypt Test",
        shopify_domain="decrypt.myshopify.com",
        shopify_access_token=original_token
    )
    
    decrypted = service.get_decrypted_access_token(tenant.id)
    assert decrypted == original_token


def test_update_sync_status(db_session):
    from datetime import datetime
    service = TenantService(db_session)
    
    tenant = service.register_tenant(
        name="Sync Test",
        shopify_domain="sync.myshopify.com",
        shopify_access_token="token"
    )
    
    sync_time = datetime.utcnow()
    updated = service.update_sync_status(tenant.id, sync_time)
    
    assert updated.last_synced_at is not None
    assert updated.last_synced_at == sync_time


def test_deactivate_tenant(db_session):
    service = TenantService(db_session)
    
    tenant = service.register_tenant(
        name="Deactivate Test",
        shopify_domain="deactivate.myshopify.com",
        shopify_access_token="token"
    )
    
    assert tenant.status == "active"
    
    deactivated = service.deactivate_tenant(tenant.id)
    assert deactivated.status == "suspended"


def test_reactivate_tenant(db_session):
    service = TenantService(db_session)
    
    tenant = service.register_tenant(
        name="Reactivate Test",
        shopify_domain="reactivate.myshopify.com",
        shopify_access_token="token"
    )
    
    service.deactivate_tenant(tenant.id)
    reactivated = service.reactivate_tenant(tenant.id)
    
    assert reactivated.status == "active"


def test_get_active_tenants(db_session):
    service = TenantService(db_session)
    
    service.register_tenant("Active1", "active1.myshopify.com", "token1")
    service.register_tenant("Active2", "active2.myshopify.com", "token2")
    tenant3 = service.register_tenant("Active3", "active3.myshopify.com", "token3")
    
    service.deactivate_tenant(tenant3.id)
    
    active = service.get_active_tenants()
    assert len(active) == 2