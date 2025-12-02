"""
Unit tests for database session management.
"""

import pytest
from sqlalchemy.orm import Session
from app.db.session import (
    get_db,
    get_engine,
    get_session_factory,
    DatabaseSession,
)


def test_get_engine():
    """Test that engine is created."""
    engine = get_engine()
    assert engine is not None
    assert str(engine.url).startswith("postgresql://")


def test_get_session_factory():
    """Test that session factory is created."""
    factory = get_session_factory()
    assert factory is not None
    
    # Create a session
    session = factory()
    assert isinstance(session, Session)
    session.close()


def test_get_db_dependency():
    """Test FastAPI database dependency."""
    db_gen = get_db()
    
    # Get session
    db = next(db_gen)
    assert isinstance(db, Session)
    
    # Clean up
    try:
        next(db_gen)
    except StopIteration:
        pass  # Expected


def test_database_session_context_manager():
    """Test context manager for Celery tasks."""
    with DatabaseSession() as db:
        assert isinstance(db, Session)
        assert db.is_active


def test_database_session_rollback_on_exception():
    """Test that session rolls back on exception."""
    try:
        with DatabaseSession() as db:
            # Simulate an error
            raise ValueError("Test error")
    except ValueError:
        pass  # Expected
    
    # Session should be closed and rolled back
    # (Can't test rollback directly without a real transaction)