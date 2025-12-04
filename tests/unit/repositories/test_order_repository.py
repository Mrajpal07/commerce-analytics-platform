import pytest
from decimal import Decimal
from datetime import datetime
from app.repositories import OrderRepository, TenantRepository
from app.models import Order, Tenant


def test_upsert_creates_new_order(db_session):
    tenant_repo = TenantRepository(db_session)
    tenant = tenant_repo.create(Tenant(
        name="Test",
        shopify_domain="test.myshopify.com",
        shopify_access_token="token",
        status="active"
    ))

    order_repo = OrderRepository(db_session)
    order = order_repo.upsert(
        tenant_id=tenant.id,
        shopify_order_id=12345,
        data={
            "order_number": "1001",
            "total_price": Decimal("99.99"),
            "currency": "USD",
            "order_created_at": datetime.utcnow()
        }
    )

    assert order.id is not None
    assert order.shopify_order_id == 12345


def test_upsert_updates_existing_order(db_session):
    tenant_repo = TenantRepository(db_session)
    tenant = tenant_repo.create(Tenant(
        name="Test",
        shopify_domain="test.myshopify.com",
        shopify_access_token="token",
        status="active"
    ))

    order_repo = OrderRepository(db_session)
    order1 = order_repo.upsert(
        tenant_id=tenant.id,
        shopify_order_id=12345,
        data={
            "order_number": "1001",
            "total_price": Decimal("99.99"),
            "currency": "USD",
            "financial_status": "pending",
            "order_created_at": datetime.utcnow()
        }
    )
    order1_id = order1.id

    order2 = order_repo.upsert(
        tenant_id=tenant.id,
        shopify_order_id=12345,
        data={
            "order_number": "1001",
            "total_price": Decimal("99.99"),
            "currency": "USD",
            "financial_status": "paid",
            "order_created_at": datetime.utcnow()
        }
    )

    assert order2.id == order1_id
    assert order2.financial_status == "paid"