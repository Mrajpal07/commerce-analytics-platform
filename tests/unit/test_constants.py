"""
Unit tests for constants module.
"""

from app.core import constants


def test_constants_exist():
    """Test that core constants are defined."""
    assert hasattr(constants, 'MAX_RETRY_ATTEMPTS')
    assert hasattr(constants, 'EVENT_PROCESSING_TIMEOUT_SECONDS')
    assert hasattr(constants, 'BATCH_SIZE_EVENTS')


def test_retry_constants():
    """Test retry-related constants."""
    assert constants.MAX_RETRY_ATTEMPTS > 0
    assert constants.RETRY_BASE_DELAY_SECONDS > 0
    assert constants.RETRY_MAX_DELAY_SECONDS > constants.RETRY_BASE_DELAY_SECONDS


def test_database_constants():
    """Test database-related constants."""
    assert constants.DEFAULT_PAGE_SIZE > 0
    assert constants.MAX_PAGE_SIZE > constants.DEFAULT_PAGE_SIZE
    assert constants.BATCH_SIZE_ORDERS > 0


def test_rate_limit_constants():
    """Test rate limiting constants."""
    assert constants.RATE_LIMIT_PER_MINUTE > 0
    assert constants.RATE_LIMIT_PER_HOUR > constants.RATE_LIMIT_PER_MINUTE


def test_shopify_constants():
    """Test Shopify integration constants."""
    assert constants.SHOPIFY_API_VERSION.startswith("202")  # Year format
    assert constants.SHOPIFY_RATE_LIMIT_PER_SECOND > 0
    assert constants.SHOPIFY_SYNC_BATCH_SIZE > 0


def test_security_constants():
    """Test security-related constants."""
    assert constants.PASSWORD_MIN_LENGTH >= 8
    assert constants.PASSWORD_MAX_LENGTH > constants.PASSWORD_MIN_LENGTH
    assert constants.JWT_ACCESS_TOKEN_EXPIRE_MINUTES > 0
    assert constants.JWT_REFRESH_TOKEN_EXPIRE_DAYS > 0


def test_monitoring_constants():
    """Test monitoring and alert constants."""
    assert constants.METRICS_COLLECTION_INTERVAL_SECONDS > 0
    assert constants.ALERT_THRESHOLD_EVENT_LAG > 0
    assert constants.ALERT_THRESHOLD_DEAD_LETTER > 0


def test_celery_constants():
    """Test Celery task constants."""
    assert constants.CELERY_TASK_SOFT_TIME_LIMIT < constants.CELERY_TASK_HARD_TIME_LIMIT
    assert constants.CELERY_TASK_MAX_RETRIES > 0
    assert constants.CELERY_QUEUE_INGESTION
    assert constants.CELERY_QUEUE_SYNC
    assert constants.CELERY_QUEUE_ANALYTICS


def test_business_logic_constants():
    """Test business logic constants."""
    assert constants.MIN_ORDER_AMOUNT_CENTS >= 0
    assert constants.MAX_ORDER_AMOUNT_CENTS > constants.MIN_ORDER_AMOUNT_CENTS
    assert constants.DEFAULT_CURRENCY in constants.SUPPORTED_CURRENCIES
    assert len(constants.SUPPORTED_CURRENCIES) > 0


def test_system_limit_constants():
    """Test system limit constants (INV-8)."""
    assert constants.MAX_ORDERS_PER_SECOND == 200  # From architecture doc
    assert constants.BURST_DURATION_SECONDS == 60  # From architecture doc
    assert constants.MAX_ORDERS_PER_BULK_WEBHOOK == 10_000  # From architecture doc


def test_http_status_codes():
    """Test HTTP status code constants."""
    assert constants.HTTP_200_OK == 200
    assert constants.HTTP_201_CREATED == 201
    assert constants.HTTP_400_BAD_REQUEST == 400
    assert constants.HTTP_401_UNAUTHORIZED == 401
    assert constants.HTTP_500_INTERNAL_SERVER_ERROR == 500


def test_error_messages():
    """Test error message constants."""
    assert isinstance(constants.ERROR_GENERIC, str)
    assert isinstance(constants.ERROR_UNAUTHORIZED, str)
    assert isinstance(constants.ERROR_NOT_FOUND, str)
    assert len(constants.ERROR_GENERIC) > 0


def test_regex_patterns():
    """Test regex pattern constants."""
    assert constants.EMAIL_REGEX
    assert constants.SHOPIFY_DOMAIN_REGEX
    assert constants.CORRELATION_ID_REGEX


def test_constants_immutability():
    """Test that constants are appropriate types."""
    # Integers
    assert isinstance(constants.MAX_RETRY_ATTEMPTS, int)
    assert isinstance(constants.DEFAULT_PAGE_SIZE, int)
    
    # Strings
    assert isinstance(constants.DEFAULT_CURRENCY, str)
    assert isinstance(constants.SHOPIFY_API_VERSION, str)
    
    # Lists
    assert isinstance(constants.SUPPORTED_CURRENCIES, list)