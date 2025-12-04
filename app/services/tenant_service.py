from typing import Optional
from sqlalchemy.orm import Session
from app.models import Tenant
from app.repositories import TenantRepository
from app.core.security import encrypt_token, decrypt_token
from app.core.exceptions import (
    ValidationException,
    NotFoundException,
    ConflictException
)
from datetime import datetime


class TenantService:
    def __init__(self, db: Session):
        self.db = db
        self.tenant_repo = TenantRepository(db)
    
    def register_tenant(
        self,
        name: str,
        shopify_domain: str,
        shopify_access_token: str,
        webhook_secret: Optional[str] = None
    ) -> Tenant:
        # Validate domain format
        if not shopify_domain or not shopify_domain.endswith('.myshopify.com'):
            raise ValidationException(
                "Invalid Shopify domain format",
                details={"shopify_domain": shopify_domain}
            )
        
        # Check if tenant already exists
        existing = self.tenant_repo.get_by_domain(shopify_domain)
        if existing:
            raise ConflictException(
                message=f"Tenant with domain '{shopify_domain}' already exists",
                error_code="TENANT_ALREADY_EXISTS",
                details={"shopify_domain": shopify_domain}
            )
        
        # Encrypt access token
        encrypted_token = encrypt_token(shopify_access_token)
        
        # Create tenant
        tenant = Tenant(
            name=name,
            shopify_domain=shopify_domain,
            shopify_access_token=encrypted_token,
            webhook_secret=webhook_secret,
            status="active"
        )
        
        created_tenant = self.tenant_repo.create(tenant)
        self.db.commit()
        
        return created_tenant
    
    def get_tenant(self, tenant_id: int) -> Tenant:
        tenant = self.tenant_repo.get(tenant_id)
        if not tenant:
            raise NotFoundException(resource_type="Tenant", identifier=tenant_id)
        return tenant
    
    def get_tenant_by_domain(self, shopify_domain: str) -> Tenant:
        tenant = self.tenant_repo.get_by_domain(shopify_domain)
        if not tenant:
            raise NotFoundException(resource_type="Tenant", identifier=shopify_domain)
        return tenant
    
    def get_decrypted_access_token(self, tenant_id: int) -> str:
        tenant = self.get_tenant(tenant_id)
        return decrypt_token(tenant.shopify_access_token)
    
    def update_sync_status(self, tenant_id: int, last_synced_at: datetime) -> Tenant:
        tenant = self.get_tenant(tenant_id)
        tenant.last_synced_at = last_synced_at
        
        updated_tenant = self.tenant_repo.update(tenant)
        self.db.commit()
        
        return updated_tenant
    
    def deactivate_tenant(self, tenant_id: int) -> Tenant:
        tenant = self.get_tenant(tenant_id)
        tenant.status = "suspended"
        
        updated_tenant = self.tenant_repo.update(tenant)
        self.db.commit()
        
        return updated_tenant
    
    def reactivate_tenant(self, tenant_id: int) -> Tenant:
        tenant = self.get_tenant(tenant_id)
        tenant.status = "active"
        
        updated_tenant = self.tenant_repo.update(tenant)
        self.db.commit()
        
        return updated_tenant
    
    def get_active_tenants(self) -> list[Tenant]:
        return self.tenant_repo.get_active_tenants()