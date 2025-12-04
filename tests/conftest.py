import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

# Valid base64-encoded 32-byte key for Fernet
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"
os.environ["JWT_SECRET_KEY"] = "Mffes6zNTzWq8dBqbAfTS_x942oEkDvB0P3CgP8YstE"
os.environ["FERNET_ENCRYPTION_KEY"] = "r9IYhjOcgRj1cAajIeVERgLjQyUAqf0ZzA9Kc1yyn-A="
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
os.environ["APP_ENV"] = "testing"
os.environ["LOG_LEVEL"] = "INFO"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)