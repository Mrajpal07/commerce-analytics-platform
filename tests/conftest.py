"""
Pytest configuration and fixtures.

IMPORTANT: Environment variables must be set BEFORE any app imports.
"""

import os

# ============================================================================
# SET ENVIRONMENT VARIABLES FIRST - BEFORE ANY IMPORTS
# ============================================================================

# Set all required env vars immediately
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-minimum-32-characters-long-for-testing-purposes-only"
os.environ["FERNET_ENCRYPTION_KEY"] = "r9IYhjOcgRj1cAajIeVERgLjQyUAqf0ZzA9Kc1yyn-A="
os.environ["APP_ENV"] = "testing"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
os.environ["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/1"

# Now it's safe to import
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))