"""
Tenant Model

Represents a tenant (customer) in the multi-tenant system.
Each tenant has their own isolated data.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime

from app.models.base import Base, BaseModel


class Tenant(BaseModel, Base):
    """
    Tenant Model
    
    Represents a customer/organization using the platform.
    All multi-tenant tables reference this via tenant_id.
    
    Attributes:
        name: Tenant display name
        shopify_domain: Shopify store domain (e.g., "mystore.myshopify.com")
        shopify_access_token: Encrypted Shopify API access token
        webhook_secret: Secret for verifying Shopify webhooks
        status: Tenant status (active, suspended, etc.)
        last_synced_at: Last successful data sync timestamp
    """
    
    __tablename__ = "tenants"
    
    # Basic information
    name = Column(
        String(255),
        nullable=False,
        doc="Tenant display name"
    )
    
    shopify_domain = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Shopify store domain (e.g., 'mystore.myshopify.com')"
    )
    
    shopify_access_token = Column(
        Text,
        nullable=False,
        doc="Encrypted Shopify API access token"
    )
    
    webhook_secret = Column(
        Text,
        nullable=True,
        doc="Secret for verifying Shopify webhook signatures"
    )
    
    status = Column(
        String(50),
        nullable=False,
        default="active",
        index=True,
        doc="Tenant status (active, suspended, deleted)"
    )
    
    last_synced_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Last successful data synchronization timestamp"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Tenant(id={self.id}, name='{self.name}', domain='{self.shopify_domain}')>"