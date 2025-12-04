from typing import Optional, Dict, Any
from decimal import Decimal
from sqlalchemy import Column, BigInteger, String, Integer, Numeric, Index
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel, TenantMixin


class Customer(BaseModel, TenantMixin, Base):
    __tablename__ = "customers"
    
    shopify_customer_id = Column(BigInteger, nullable=False)
    email = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    orders_count = Column(Integer, nullable=False, default=0)
    total_spent = Column(Numeric(12, 2), nullable=False, default=0)
    
    __table_args__ = (
        Index('idx_customers_unique', 'tenant_id', 'shopify_customer_id', unique=True),
        Index('idx_customers_email', 'tenant_id', 'email'),
    )
    
    def __init__(self, **kwargs):
        if 'orders_count' not in kwargs:
            kwargs['orders_count'] = 0
        if 'total_spent' not in kwargs:
            kwargs['total_spent'] = Decimal('0')
        super().__init__(**kwargs)
    
    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or "Unknown"
    
    def increment_order_count(self, amount: Decimal) -> None:
        self.orders_count += 1
        self.total_spent += amount
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'shopify_customer_id': self.shopify_customer_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'orders_count': self.orders_count,
            'total_spent': float(self.total_spent) if self.total_spent else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, email='{self.email}', tenant_id={self.tenant_id})>"