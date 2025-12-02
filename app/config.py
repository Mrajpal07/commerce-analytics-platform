"""
Configuration Management Module

Loads and validates environment variables using Pydantic Settings.
Provides singleton access to configuration throughout the application.
"""

from functools import lru_cache
from typing import Optional, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Configuration
    
    All settings are loaded from environment variables or .env file.
    Pydantic performs automatic type validation and conversion.
    """
    
    # ============================================================================
    # APPLICATION SETTINGS
    # ============================================================================
    APP_NAME: str = Field(default="commerce-analytics-platform")
    APP_ENV: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    
    # ============================================================================
    # DATABASE SETTINGS
    # ============================================================================
    DATABASE_URL: str = Field(
        ...,  # Required field
        description="PostgreSQL connection string"
    )
    DATABASE_POOL_SIZE: int = Field(default=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=10)
    DATABASE_ECHO: bool = Field(default=False)  # Log SQL queries
    
    # ============================================================================
    # REDIS SETTINGS
    # ============================================================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string"
    )
    REDIS_MAX_CONNECTIONS: int = Field(default=50)
    
    # ============================================================================
    # CELERY SETTINGS
    # ============================================================================
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/1",
        description="Celery result backend URL"
    )
    CELERY_TASK_ALWAYS_EAGER: bool = Field(
        default=False,
        description="Execute tasks synchronously (testing only)"
    )
    CELERY_TASK_SERIALIZER: str = Field(default="json")
    CELERY_RESULT_SERIALIZER: str = Field(default="json")
    CELERY_ACCEPT_CONTENT: List[str] = Field(default=["json"])
    CELERY_TIMEZONE: str = Field(default="UTC")
    CELERY_ENABLE_UTC: bool = Field(default=True)
    
    # ============================================================================
    # JWT AUTHENTICATION
    # ============================================================================
    JWT_SECRET_KEY: str = Field(
        ...,  # Required
        min_length=32,
        description="Secret key for JWT token signing (min 32 chars)"
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # ============================================================================
    # ENCRYPTION (for Shopify tokens)
    # ============================================================================
    FERNET_ENCRYPTION_KEY: str = Field(
        ...,  # Required
        description="Fernet key for encrypting sensitive data (base64 encoded)"
    )
    
    # ============================================================================
    # API CONFIGURATION
    # ============================================================================
    API_V1_PREFIX: str = Field(default="/api/v1")
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # ============================================================================
    # SHOPIFY INTEGRATION
    # ============================================================================
    SHOPIFY_API_VERSION: str = Field(
        default="2024-01",
        description="Shopify API version"
    )
    SHOPIFY_WEBHOOK_VERIFICATION_ENABLED: bool = Field(default=True)
    
    # ============================================================================
    # RATE LIMITING
    # ============================================================================
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)
    
    # ============================================================================
    # MONITORING & OBSERVABILITY
    # ============================================================================
    SENTRY_DSN: Optional[str] = Field(default=None)
    PROMETHEUS_PORT: int = Field(default=9090)
    ENABLE_METRICS: bool = Field(default=True)
    
    # ============================================================================
    # PYDANTIC CONFIGURATION
    # ============================================================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra env vars
    )
    
    # ============================================================================
    # VALIDATORS
    # ============================================================================
    
    @validator("APP_ENV")
    def validate_environment(cls, v: str) -> str:
        """Ensure APP_ENV is one of the allowed values."""
        allowed = {"development", "production", "testing", "staging"}
        if v.lower() not in allowed:
            raise ValueError(f"APP_ENV must be one of {allowed}, got '{v}'")
        return v.lower()
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        """Ensure LOG_LEVEL is valid."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}, got '{v}'")
        return v_upper
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """Ensure DATABASE_URL starts with postgresql://"""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError(
                "DATABASE_URL must start with 'postgresql://' or 'postgresql+asyncpg://'"
            )
        return v
    
    @validator("JWT_SECRET_KEY")
    def validate_jwt_secret(cls, v: str) -> str:
        """Ensure JWT secret is strong enough."""
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("CORS_ORIGINS")
    def parse_cors_origins(cls, v: str) -> str:
        """Validate CORS origins format."""
        origins = [origin.strip() for origin in v.split(",")]
        for origin in origins:
            if not origin.startswith(("http://", "https://")):
                raise ValueError(f"Invalid CORS origin: {origin}")
        return v
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENV == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.APP_ENV == "development"
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.APP_ENV == "testing"
    
    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    def get_database_url_sync(self) -> str:
        """Get synchronous database URL (for SQLAlchemy)."""
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    def get_database_url_async(self) -> str:
        """Get async database URL (for asyncpg)."""
        if "postgresql+asyncpg://" in self.DATABASE_URL:
            return self.DATABASE_URL
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are loaded only once
    and reused throughout the application lifecycle.
    
    Returns:
        Settings: Validated configuration object
    
    Example:
        >>> from app.config import get_settings
        >>> config = get_settings()
        >>> print(config.DATABASE_URL)
    """
    return Settings()


# Convenience export
settings = get_settings()