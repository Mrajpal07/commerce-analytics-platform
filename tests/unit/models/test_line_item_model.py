import pytest
from decimal import Decimal
from app.models import LineItem


def test_line_item_creation():
    item = LineItem(
        tenant_id=1,
        order_id=100,
        product_id=999,
        title="Test Product",
        quantity=2,
        price=Decimal("49.99")
    )
    
    assert item.order_id == 100
    assert item.product_id == 999
    assert item.quantity == 2
    assert item.price == Decimal("49.99")


def test_line_item_subtotal():
    item = LineItem(
        tenant_id=1,
        order_id=100,
        title="Test Product",
        quantity=3,
        price=Decimal("25.00")
    )
    
    assert item.subtotal == Decimal("75.00")


def test_line_item_to_dict():
    item = LineItem(
        id=1,
        tenant_id=10,
        order_id=100,
        product_id=999,
        title="Test Product",
        quantity=2,
        price=Decimal("49.99")
    )
    
    result = item.to_dict()
    
    assert result['order_id'] == 100
    assert result['title'] == "Test Product"
    assert result['quantity'] == 2
    assert result['subtotal'] == 99.98