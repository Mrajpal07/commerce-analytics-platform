"""
Database Session Management

Provides SQLAlchemy engine, session factory, and FastAPI dependency
for database access throughout the application.
"""

from typing import Generator
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

from app.config import get_settings

# Get configuration
config = get_settings()

# ============================================================================
# ENGINE CONFIGURATION
# ============================================================================

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    config.get_database_url_sync(),
    pool_size=config.DATABASE_POOL_SIZE,
    max_overflow=config.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=config.DATABASE_ECHO,  # Log SQL queries (development only)
)


# ============================================================================
# SESSION FACTORY
# ============================================================================

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,  # Manual transaction control
    autoflush=False,   # Manual flush control
    bind=engine,
    expire_on_commit=False,  # Don't expire objects after commit
)


# ============================================================================
# POSTGRESQL-SPECIFIC OPTIMIZATIONS
# ============================================================================

@event.listens_for(Engine, "connect")
def set_postgresql_pragmas(dbapi_conn, connection_record):
    """
    Set PostgreSQL connection parameters for optimal performance.
    
    This runs once per new connection.
    """
    cursor = dbapi_conn.cursor()
    
    # Set statement timeout (30 seconds)
    cursor.execute("SET statement_timeout = '30s'")
    
    # Set timezone to UTC
    cursor.execute("SET timezone = 'UTC'")
    
    cursor.close()


# ============================================================================
# FASTAPI DEPENDENCY
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    
    Automatically handles:
    - Session creation
    - Transaction commit on success
    - Rollback on exception
    - Session cleanup
    
    Usage:
        @app.get("/orders")
        def get_orders(db: Session = Depends(get_db)):
            orders = db.query(Order).all()
            return orders
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Commit transaction if no exception
    except Exception:
        db.rollback()  # Rollback on any exception
        raise
    finally:
        db.close()  # Always close session


# ============================================================================
# CONTEXT MANAGER (for scripts/tasks)
# ============================================================================

class DatabaseSession:
    """
    Context manager for database sessions in Celery tasks or scripts.
    
    Usage:
        with DatabaseSession() as db:
            order = db.query(Order).first()
            order.status = "completed"
            db.commit()
    """
    
    def __enter__(self) -> Session:
        """Create and return a new session."""
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up session on exit."""
        if exc_type is not None:
            # Exception occurred - rollback
            self.db.rollback()
        else:
            # Success - commit
            self.db.commit()
        
        # Always close
        self.db.close()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_engine() -> Engine:
    """
    Get the SQLAlchemy engine instance.
    
    Returns:
        Engine: SQLAlchemy engine
    """
    return engine


def get_session_factory() -> sessionmaker:
    """
    Get the session factory.
    
    Returns:
        sessionmaker: Session factory
    """
    return SessionLocal


def init_db() -> None:
    """
    Initialize database (create all tables).
    
    This is used in development/testing.
    In production, use Alembic migrations instead.
    """
    from app.db.base import Base  # Import here to avoid circular imports
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all database tables.
    
    WARNING: This deletes all data. Use only in testing.
    """
    from app.db.base import Base
    Base.metadata.drop_all(bind=engine)