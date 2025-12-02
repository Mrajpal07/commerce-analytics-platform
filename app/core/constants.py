"""
Core Constants

System-wide constants, limits, and configuration defaults.
Centralizes magic numbers and business rules.
"""

# ============================================================================
# EVENT PROCESSING
# ============================================================================

# Maximum retry attempts before moving to dead letter queue
# Aligned with INV-2 (Event Idempotency) and failure mode FM-5
MAX_RETRY_ATTEMPTS = 5

# Base delay for exponential backoff (seconds)
RETRY_BASE_DELAY_SECONDS = 5

# Maximum delay for exponential backoff (seconds)
RETRY_MAX_DELAY_SECONDS = 300  # 5 minutes

# Event processing timeout (seconds)
EVENT_PROCESSING_TIMEOUT_SECONDS = 300  # 5 minutes

# Maximum events to process in single batch
BATCH_SIZE_EVENTS = 100

# Reconciliation interval (seconds)
RECONCILIATION_INTERVAL_SECONDS = 900  # 15 minutes


# ============================================================================
# DATABASE
# ============================================================================

# Default pagination limit
DEFAULT_PAGE_SIZE = 50

# Maximum pagination limit (prevent excessive queries)
MAX_PAGE_SIZE = 1000

# Batch size for bulk inserts
BATCH_SIZE_ORDERS = 500
BATCH_SIZE_CUSTOMERS = 1000
BATCH_SIZE_PRODUCTS = 500

# Query timeout (seconds)
QUERY_TIMEOUT_SECONDS = 30

# Materialized view refresh interval (seconds)
MATERIALIZED_VIEW_REFRESH_INTERVAL_SECONDS = 300  # 5 minutes


# ============================================================================
# API RATE LIMITING
# ============================================================================

# Requests per minute per tenant
RATE_LIMIT_PER_MINUTE = 60

# Requests per hour per tenant
RATE_LIMIT_PER_HOUR = 1000

# Burst tolerance (requests allowed in short spike)
RATE_LIMIT_BURST = 10


# ============================================================================
# SHOPIFY INTEGRATION
# ============================================================================

# Shopify API version
SHOPIFY_API_VERSION = "2024-01"

# Shopify rate limit (requests per second)
SHOPIFY_RATE_LIMIT_PER_SECOND = 2

# Shopify webhook timeout (seconds)
SHOPIFY_WEBHOOK_TIMEOUT_SECONDS = 5

# Shopify API retry delay after rate limit (seconds)
SHOPIFY_RATE_LIMIT_RETRY_DELAY = 60

# Maximum orders to sync in single request
SHOPIFY_SYNC_BATCH_SIZE = 250

# Shopify request timeout (seconds)
SHOPIFY_REQUEST_TIMEOUT_SECONDS = 30


# ============================================================================
# SECURITY
# ============================================================================

# JWT access token expiry (minutes)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15

# JWT refresh token expiry (days)
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

# Minimum password length
PASSWORD_MIN_LENGTH = 8

# Maximum password length
PASSWORD_MAX_LENGTH = 128

# Password must contain uppercase
PASSWORD_REQUIRE_UPPERCASE = True

# Password must contain lowercase
PASSWORD_REQUIRE_LOWERCASE = True

# Password must contain digit
PASSWORD_REQUIRE_DIGIT = True

# Password must contain special character
PASSWORD_REQUIRE_SPECIAL = True

# Failed login attempts before lockout
MAX_FAILED_LOGIN_ATTEMPTS = 5

# Account lockout duration (minutes)
ACCOUNT_LOCKOUT_DURATION_MINUTES = 15


# ============================================================================
# MONITORING & OBSERVABILITY
# ============================================================================

# Metrics collection interval (seconds)
METRICS_COLLECTION_INTERVAL_SECONDS = 60

# Alert threshold: Event processing lag (number of pending events)
ALERT_THRESHOLD_EVENT_LAG = 100

# Alert threshold: Dead letter queue depth
ALERT_THRESHOLD_DEAD_LETTER = 10

# Alert threshold: API response time (milliseconds)
ALERT_THRESHOLD_API_LATENCY_MS = 5000

# Alert threshold: Database connection pool usage (percentage)
ALERT_THRESHOLD_DB_POOL_USAGE = 90

# Health check timeout (seconds)
HEALTH_CHECK_TIMEOUT_SECONDS = 5


# ============================================================================
# CELERY TASK CONFIGURATION
# ============================================================================

# Celery task soft time limit (seconds)
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes

# Celery task hard time limit (seconds)
CELERY_TASK_HARD_TIME_LIMIT = 600  # 10 minutes

# Celery task max retries
CELERY_TASK_MAX_RETRIES = 3

# Celery queue names
CELERY_QUEUE_INGESTION = "ingestion"  # High priority
CELERY_QUEUE_SYNC = "sync"  # Medium priority
CELERY_QUEUE_ANALYTICS = "analytics"  # Low priority

# Celery task priorities
CELERY_PRIORITY_HIGH = 9
CELERY_PRIORITY_MEDIUM = 5
CELERY_PRIORITY_LOW = 1


# ============================================================================
# DATA RETENTION
# ============================================================================

# Event log retention (days)
EVENT_LOG_RETENTION_DAYS = 365

# Metrics retention (days)
METRICS_RETENTION_DAYS = 730  # 2 years

# Audit log retention (days)
AUDIT_LOG_RETENTION_DAYS = 2555  # 7 years

# Completed event cleanup threshold (days)
COMPLETED_EVENT_CLEANUP_DAYS = 90


# ============================================================================
# BUSINESS LOGIC
# ============================================================================

# Minimum order amount (cents)
MIN_ORDER_AMOUNT_CENTS = 0

# Maximum order amount (cents) - for fraud detection
MAX_ORDER_AMOUNT_CENTS = 100_000_00  # $100,000

# Currency code
DEFAULT_CURRENCY = "USD"

# Supported currencies
SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP", "CAD", "AUD"]

# Maximum line items per order
MAX_LINE_ITEMS_PER_ORDER = 100


# ============================================================================
# SYSTEM LIMITS (INV-8: Burst Tolerance)
# ============================================================================

# Maximum orders per second (burst)
MAX_ORDERS_PER_SECOND = 200

# Burst duration tolerance (seconds)
BURST_DURATION_SECONDS = 60

# Maximum orders per bulk webhook
MAX_ORDERS_PER_BULK_WEBHOOK = 10_000

# Maximum concurrent tasks per worker
MAX_CONCURRENT_TASKS = 4


# ============================================================================
# ERROR MESSAGES
# ============================================================================

# Generic error messages (avoid exposing internal details)
ERROR_GENERIC = "An error occurred. Please try again later."
ERROR_UNAUTHORIZED = "Authentication required."
ERROR_FORBIDDEN = "You do not have permission to access this resource."
ERROR_NOT_FOUND = "The requested resource was not found."
ERROR_RATE_LIMIT = "Rate limit exceeded. Please try again later."
ERROR_VALIDATION = "Invalid input provided."


# ============================================================================
# HTTP STATUS CODES (for reference)
# ============================================================================

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_202_ACCEPTED = 202
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409
HTTP_429_TOO_MANY_REQUESTS = 429
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_502_BAD_GATEWAY = 502
HTTP_503_SERVICE_UNAVAILABLE = 503


# ============================================================================
# REGEX PATTERNS
# ============================================================================

# Email validation pattern
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Shopify domain pattern
SHOPIFY_DOMAIN_REGEX = r'^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$'

# Correlation ID pattern (UUID v4)
CORRELATION_ID_REGEX = r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$'