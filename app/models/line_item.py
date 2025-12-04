from typing import Dict, Any
from decimal import Decimal
from sqlalchemy import Column, BigInteger, String, Integer, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel, TenantMixin


class LineItem(BaseModel, TenantMixin, Base):
    __tablename__ = "line_items"
    
    order_id = Column(BigInteger, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(BigInteger, nullable=True)
    variant_id = Column(BigInteger, nullable=True)
    title = Column(String(500), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    
    order = relationship("Order", backref="line_items")
    
    __table_args__ = (
        Index('idx_line_items_order', 'order_id'),
        Index('idx_line_items_product', 'tenant_id', 'product_id'),
    )
    
    @property
    def subtotal(self) -> Decimal:
        return self.price * self.quantity
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'variant_id': self.variant_id,
            'title': self.title,
            'quantity': self.quantity,
            'price': float(self.price) if self.price else None,
            'subtotal': float(self.subtotal),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<LineItem(id={self.id}, title='{self.title}', quantity={self.quantity})>"