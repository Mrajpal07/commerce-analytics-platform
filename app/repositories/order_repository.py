from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Order
from app.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        super().__init__(Order, db)
    
    def get_by_shopify_id(self, tenant_id: int, shopify_order_id: int) -> Optional[Order]:
        return self.db.query(Order).filter(
            Order.tenant_id == tenant_id,
            Order.shopify_order_id == shopify_order_id
        ).first()
    
    def upsert(self, tenant_id: int, shopify_order_id: int, data: dict) -> Order:
        order = self.get_by_shopify_id(tenant_id, shopify_order_id)
        if order:
            for key, value in data.items():
                setattr(order, key, value)
        else:
            order = Order(tenant_id=tenant_id, shopify_order_id=shopify_order_id, **data)
            self.db.add(order)
        self.db.flush()
        self.db.refresh(order)
        return order
    
    def get_by_date_range(self, tenant_id: int, start_date: datetime, end_date: datetime) -> List[Order]:
        return self.db.query(Order).filter(
            and_(
                Order.tenant_id == tenant_id,
                Order.order_created_at >= start_date,
                Order.order_created_at <= end_date
            )
        ).order_by(Order.order_created_at.desc()).all()