import pytest
from datetime import datetime
from decimal import Decimal
from app.models import Order
from app.models.order import FinancialStatus, FulfillmentStatus


def test_order_creation():
    order = Order(
        tenant_id=1,
        shopify_order_id=12345,
        order_number="1001",
        total_price=Decimal("99.99"),
        order_created_at=datetime(2024, 12, 1, 10, 0, 0)
    )
    
    assert order.tenant_id == 1
    assert order.shopify_order_id == 12345
    assert order.total_price == Decimal("99.99")
    assert order.currency == "USD"


def test_order_with_customer():
    order = Order(
        tenant_id=1,
        shopify_order_id=12345,
        order_number="1001",
        customer_id=999,
        email="customer@example.com",
        total_price=Decimal("150.00"),
        order_created_at=datetime.utcnow()
    )
    
    assert order.customer_id == 999
    assert order.email == "customer@example.com"


def test_order_is_paid():
    order = Order(
        tenant_id=1,
        shopify_order_id=12345,
        order_number="1001",
        total_price=Decimal("99.99"),
        financial_status=FinancialStatus.PAID.value,
        order_created_at=datetime.utcnow()
    )
    
    assert order.is_paid is True


def test_order_is_not_paid():
    order = Order(
        tenant_id=1,
        shopify_order_id=12345,
        order_number="1001",
        total_price=Decimal("99.99"),
        financial_status=FinancialStatus.PENDING.value,
        order_created_at=datetime.utcnow()
    )
    
    assert order.is_paid is False


def test_order_is_fulfilled():
    order = Order(
        tenant_id=1,
        shopify_order_id=12345,
        order_number="1001",
        total_price=Decimal("99.99"),
        fulfillment_status=FulfillmentStatus.FULFILLED.value,
        order_created_at=datetime.utcnow()
    )
    
    assert order.is_fulfilled is True


def test_order_to_dict():
    order = Order(
        id=1,
        tenant_id=10,
        shopify_order_id=12345,
        order_number="1001",
        total_price=Decimal("99.99"),
        currency="USD",
        order_created_at=datetime(2024, 12, 1, 10, 0, 0)
    )
    order.created_at = datetime(2024, 12, 1, 10, 0, 0)
    order.updated_at = datetime(2024, 12, 1, 10, 0, 0)
    
    result = order.to_dict()
    
    assert result['id'] == 1
    assert result['shopify_order_id'] == 12345
    assert result['total_price'] == 99.99
    assert result['currency'] == "USD"


def test_order_repr():
    order = Order(
        id=1,
        tenant_id=10,
        shopify_order_id=12345,
        order_number="1001",
        total_price=Decimal("99.99"),
        order_created_at=datetime.utcnow()
    )
    
    repr_str = repr(order)
    
    assert "Order" in repr_str
    assert "1001" in repr_str
    assert "tenant_id=10" in repr_str