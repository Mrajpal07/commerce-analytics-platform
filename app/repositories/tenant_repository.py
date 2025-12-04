from typing import Optional
from sqlalchemy.orm import Session
from app.models import Tenant
from app.repositories.base_repository import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    def __init__(self, db: Session):
        super().__init__(Tenant, db)
    
    def get_by_domain(self, shopify_domain: str) -> Optional[Tenant]:
        return self.db.query(Tenant).filter(
            Tenant.shopify_domain == shopify_domain
        ).first()
    
    def get_active_tenants(self) -> list[Tenant]:
        return self.db.query(Tenant).filter(
            Tenant.status == "active"
        ).all()