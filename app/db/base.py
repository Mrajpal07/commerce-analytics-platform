"""
Database Base Configuration

Re-exports Base from models.base for backward compatibility.
"""

from app.models.base import Base

__all__ = ["Base"]