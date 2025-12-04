from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, BigInteger, String, Numeric, DateTime, Index
from sqlalchemy.orm import relationship
from enum import Enum

from app.models.base import Base, BaseModel, TenantMixin


class FinancialStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    PARTIALLY_REFUNDED = "partially_refunded"
    REFUNDED = "refunded"
    VOIDED = "voided"


class FulfillmentStatus(str, Enum):
    FULFILLED = "fulfilled"
    PARTIAL = "partial"
    UNFULFILLED = "unfulfilled"
    RESTOCKED = "restocked"


class Order(BaseModel, TenantMixin, Base):
    __tablename__ = "orders"
    
    shopify_order_id = Column(BigInteger, nullable=False)
    order_number = Column(String(50), nullable=False)
    customer_id = Column(BigInteger, nullable=True)
    email = Column(String(255), nullable=True)
    total_price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    financial_status = Column(String(50), nullable=True)
    fulfillment_status = Column(String(50), nullable=True)
    order_created_at = Column(DateTime(timezone=True), nullable=False)
    
    __table_args__ = (
        Index('idx_orders_unique', 'tenant_id', 'shopify_order_id', unique=True),
        Index('idx_orders_tenant_date', 'tenant_id', 'order_created_at'),
        Index('idx_orders_customer', 'tenant_id', 'customer_id'),
        Index('idx_orders_email', 'tenant_id', 'email'),
    )
    
    def __init__(self, **kwargs):
        if 'currency' not in kwargs:
            kwargs['currency'] = 'USD'
        super().__init__(**kwargs)
    
    @property
    def is_paid(self) -> bool:
        return self.financial_status == FinancialStatus.PAID.value
    
    @property
    def is_fulfilled(self) -> bool:
        return self.fulfillment_status == FulfillmentStatus.FULFILLED.value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'shopify_order_id': self.shopify_order_id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'email': self.email,
            'total_price': float(self.total_price) if self.total_price else None,
            'currency': self.currency,
            'financial_status': self.financial_status,
            'fulfillment_status': self.fulfillment_status,
            'order_created_at': self.order_created_at.isoformat() if self.order_created_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<Order(id={self.id}, order_number='{self.order_number}', tenant_id={self.tenant_id})>"