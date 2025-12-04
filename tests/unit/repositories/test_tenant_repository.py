import pytest
from app.repositories import TenantRepository
from app.models import Tenant


def test_create_and_get_tenant(db_session):
    repo = TenantRepository(db_session)
    tenant = Tenant(
        name="Test Store",
        shopify_domain="test.myshopify.com",
        shopify_access_token="token123",
        status="active"
    )
    created = repo.create(tenant)
    assert created.id is not None

    fetched = repo.get(created.id)
    assert fetched.shopify_domain == "test.myshopify.com"


def test_get_by_domain(db_session):
    repo = TenantRepository(db_session)
    tenant = Tenant(
        name="Domain Test",
        shopify_domain="domain-test.myshopify.com",
        shopify_access_token="token456",
        status="active"
    )
    repo.create(tenant)

    found = repo.get_by_domain("domain-test.myshopify.com")
    assert found is not None
    assert found.name == "Domain Test"