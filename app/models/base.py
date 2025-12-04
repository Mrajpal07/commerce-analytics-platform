"""
Database Base Models

Provides base classes with common fields and tenant isolation support.
"""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, BigInteger, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import declared_attr, relationship, declarative_base

# Create declarative base
Base = declarative_base()


class BaseModel:
    """
    Base model with common fields for all tables.
    
    Provides:
    - Primary key (id)
    - Timestamps (created_at, updated_at)
    - Common utilities (repr, to_dict)
    
    This is a mixin, not a real table.
    """
    
    # Primary key
    # Use Integer for SQLite compatibility (autoincrement), BigInteger for PostgreSQL
    id = Column(Integer().with_variant(BigInteger, "postgresql"), primary_key=True, index=True, autoincrement=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        doc="Record creation timestamp (UTC)"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Record last update timestamp (UTC)"
    )
    
    def __repr__(self) -> str:
        """
        String representation of model instance.
        
        Returns:
            str: Model name and ID
        """
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Useful for JSON serialization and debugging.
        Excludes SQLAlchemy internal attributes.
        
        Returns:
            Dict[str, Any]: Dictionary representation of model
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Convert datetime to ISO format string
            if isinstance(value, datetime):
                value = value.isoformat()
            
            result[column.name] = value
        
        return result


class TenantMixin:
    """
    Mixin for multi-tenant tables.
    
    Adds tenant_id foreign key and relationship to Tenant model.
    Enforces INV-3: Tenant Isolation.
    
    Usage:
        class Order(BaseModel, TenantMixin, Base):
            __tablename__ = "orders"
            # Gets tenant_id automatically
    
    IMPORTANT: Models using this mixin MUST:
    1. Add index on (tenant_id, ...) for performance
    2. Always filter by tenant_id in queries
    3. Use Row-Level Security (RLS) in PostgreSQL
    """
    
    @declared_attr
    def tenant_id(cls):
        """
        Foreign key to tenants table.
        
        Uses @declared_attr to ensure proper column creation
        in each inheriting model's table.
        """
        return Column(
            Integer,
            ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,  # Index for query performance
            doc="Reference to tenant that owns this record"
        )
    
    @declared_attr
    def tenant(cls):
        """
        Relationship to Tenant model.
        
        Allows accessing tenant data:
            order.tenant.name
            order.tenant.shopify_domain
        """
        return relationship(
            "Tenant",
            foreign_keys=[cls.tenant_id],
            lazy="joined",  # Eager load tenant data to reduce queries
            viewonly=True  # Don't establish back-reference (simplifies)
        )
    
    @declared_attr
    def __table_args__(cls):
        """
        Add composite index on (tenant_id, created_at) for common queries.
        
        This optimizes queries like:
            SELECT * FROM orders WHERE tenant_id = ? ORDER BY created_at DESC
        """
        return (
            Index(f"ix_{cls.__tablename__}_tenant_created", "tenant_id", "created_at"),
        )


class TimestampMixin:
    """
    Alternative mixin that ONLY provides timestamps (no id).
    
    Use this for join tables or tables where you want custom primary keys.
    
    Usage:
        class OrderLineItem(TimestampMixin, Base):
            __tablename__ = "order_line_items"
            order_id = Column(BigInteger, ForeignKey("orders.id"), primary_key=True)
            product_id = Column(BigInteger, primary_key=True)
    """
    
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_tenant_filter(tenant_id: int) -> Dict[str, int]:
    """
    Helper function to create tenant filter for queries.
    
    Args:
        tenant_id: Tenant ID to filter by
    
    Returns:
        Dict with tenant_id filter
    
    Usage:
        db.query(Order).filter_by(**get_tenant_filter(tenant_id)).all()
    """
    return {"tenant_id": tenant_id}