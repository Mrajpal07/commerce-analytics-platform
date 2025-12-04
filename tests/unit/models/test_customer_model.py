import pytest
from decimal import Decimal
from app.models import Customer


def test_customer_creation():
    customer = Customer(
        tenant_id=1,
        shopify_customer_id=12345,
        email="customer@example.com",
        first_name="John",
        last_name="Doe"
    )
    
    assert customer.shopify_customer_id == 12345
    assert customer.email == "customer@example.com"
    assert customer.orders_count == 0
    assert customer.total_spent == Decimal('0')


def test_customer_full_name():
    customer = Customer(
        tenant_id=1,
        shopify_customer_id=12345,
        first_name="John",
        last_name="Doe"
    )
    
    assert customer.full_name == "John Doe"


def test_customer_full_name_first_only():
    customer = Customer(
        tenant_id=1,
        shopify_customer_id=12345,
        first_name="John"
    )
    
    assert customer.full_name == "John"


def test_customer_increment_order_count():
    customer = Customer(
        tenant_id=1,
        shopify_customer_id=12345
    )
    
    customer.increment_order_count(Decimal("99.99"))
    
    assert customer.orders_count == 1
    assert customer.total_spent == Decimal("99.99")
    
    customer.increment_order_count(Decimal("50.00"))
    
    assert customer.orders_count == 2
    assert customer.total_spent == Decimal("149.99")


def test_customer_to_dict():
    customer = Customer(
        id=1,
        tenant_id=10,
        shopify_customer_id=12345,
        email="customer@example.com",
        first_name="John",
        last_name="Doe",
        orders_count=5,
        total_spent=Decimal("500.00")
    )
    
    result = customer.to_dict()
    
    assert result['shopify_customer_id'] == 12345
    assert result['full_name'] == "John Doe"
    assert result['orders_count'] == 5
    assert result['total_spent'] == 500.00