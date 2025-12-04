from typing import Optional
from sqlalchemy.orm import Session
from app.models import Customer
from app.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: Session):
        super().__init__(Customer, db)
    
    def get_by_shopify_id(self, tenant_id: int, shopify_customer_id: int) -> Optional[Customer]:
        return self.db.query(Customer).filter(
            Customer.tenant_id == tenant_id,
            Customer.shopify_customer_id == shopify_customer_id
        ).first()
    
    def get_by_email(self, tenant_id: int, email: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(
            Customer.tenant_id == tenant_id,
            Customer.email == email
        ).first()