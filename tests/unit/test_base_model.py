"""
Unit tests for base model mixins.
"""

import pytest
from datetime import datetime
from sqlalchemy import Column, String
from app.models.base import Base, BaseModel, TenantMixin, get_tenant_filter
from app.models import Tenant
from app.models import Base, BaseModel, TenantMixin



class DummyModel(BaseModel, Base):
    """Test model with only BaseModel."""
    __tablename__ = "dummy_model"
    name = Column(String)


class TenantModel(BaseModel, TenantMixin, Base):
    """Test model with BaseModel and TenantMixin."""
    __tablename__ = "tenant_model"
    name = Column(String)


def test_base_model_has_common_fields():
    """Test that BaseModel provides id and timestamps."""
    model = DummyModel()
    
    assert hasattr(model, 'id')
    assert hasattr(model, 'created_at')
    assert hasattr(model, 'updated_at')


def test_base_model_repr():
    """Test string representation."""
    model = DummyModel()
    model.id = 123
    
    repr_str = repr(model)
    assert "DummyModel" in repr_str
    assert "123" in repr_str


def test_base_model_to_dict():
    """Test dictionary conversion."""
    model = DummyModel()
    model.id = 1
    model.name = "Test"
    model.created_at = datetime(2024, 1, 1, 12, 0, 0)
    model.updated_at = datetime(2024, 1, 1, 12, 0, 0)
    
    result = model.to_dict()
    
    assert result['id'] == 1
    assert result['name'] == "Test"
    assert 'created_at' in result
    assert 'updated_at' in result


def test_tenant_mixin_adds_tenant_id():
    """Test that TenantMixin adds tenant_id column."""
    assert hasattr(TenantModel, 'tenant_id')


def test_tenant_mixin_adds_tenant_relationship():
    """Test that TenantMixin adds tenant relationship."""
    assert hasattr(TenantModel, 'tenant')


def test_tenant_mixin_creates_index():
    """Test that TenantMixin creates composite index."""
    # Check that table args exist
    assert hasattr(TenantModel, '__table_args__')
    
    # Get indexes
    table_args = TenantModel.__table_args__
    assert len(table_args) > 0


def test_get_tenant_filter():
    """Test tenant filter utility."""
    filter_dict = get_tenant_filter(tenant_id=42)
    
    assert filter_dict == {"tenant_id": 42}


def test_timestamps_are_datetime():
    """Test that timestamps use proper datetime type."""
    model = DummyModel()
    
    # Check column types
    created_col = DummyModel.__table__.columns['created_at']
    updated_col = DummyModel.__table__.columns['updated_at']
    
    assert created_col.type.timezone is True
    assert updated_col.type.timezone is True