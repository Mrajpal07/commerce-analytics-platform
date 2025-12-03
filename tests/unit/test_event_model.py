"""
Unit tests for Event model.
"""

import pytest
from datetime import datetime, timedelta
from app.models.event import Event, EventStatus, EventType, EntityType
from app.models import Event 



def test_event_creation():
    """Test basic event creation."""
    event = Event(
        tenant_id=1,
        event_type=EventType.ORDER_CREATED.value,
        entity_type=EntityType.ORDER.value,
        entity_id="12345",
        idempotency_key="test-key-123",
        payload={"order_id": 12345, "total": 100.00}
    )
    
    assert event.tenant_id == 1
    assert event.event_type == EventType.ORDER_CREATED.value
    assert event.status == EventStatus.PENDING.value
    assert event.retry_count == 0
    assert event.payload["order_id"] == 12345


def test_event_mark_as_processing():
    """Test marking event as processing."""
    event = Event(
        tenant_id=1,
        event_type=EventType.ORDER_CREATED.value,
        entity_type=EntityType.ORDER.value,
        entity_id="12345",
        idempotency_key="test-key-123",
        payload={}
    )
    
    event.mark_as_processing()
    assert event.status == EventStatus.PROCESSING.value


def test_event_mark_as_completed():
    """Test marking event as completed."""
    event = Event(
        tenant_id=1,
        event_type=EventType.ORDER_CREATED.value,
        entity_type=EntityType.ORDER.value,
        entity_id="12345",
        idempotency_key="test-key-123",
        payload={}
    )
    
    event.mark_as_completed()
    assert event.status == EventStatus.COMPLETED.value
    assert event.processed_at is not None


def test_event_mark_as_failed_with_retries():
    """Test marking event as failed (retriable)."""
    event = Event(
        tenant_id=1,
        event_type=EventType.ORDER_CREATED.value,
        entity_type=EntityType.ORDER.value,
        entity_id="12345",
        idempotency_key="test-key-123",
        payload={}
    )
    
    event.mark_as_failed("Test error", max_retries=5)
    
    assert event.status == EventStatus.FAILED.value
    assert event.retry_count == 1
    assert event.error_message == "Test error"
    assert event.processed_at is None  # Not terminal yet


def test_event_mark_as_failed_exceeds_max_retries():
    """Test event moves to dead letter after max retries."""
    event = Event(
        tenant_id=1,
        event_type=EventType.ORDER_CREATED.value,
        entity_type=EntityType.ORDER.value,
        entity_id="12345",
        idempotency_key="test-key-123",
        payload={},
        retry_count=4  # Already tried 4 times
    )
    
    event.mark_as_failed("Final error", max_retries=5)
    
    assert event.status == EventStatus.DEAD_LETTER.value
    assert event.retry_count == 5
    assert event.processed_at is not None


def test_event_reset_for_retry():
    """Test resetting failed event for retry."""
    event = Event(
        tenant_id=1,
        event_type=EventType.ORDER_CREATED.value,
        entity_type=EntityType.ORDER.value,
        entity_id="12345",
        idempotency_key="test-key-123",
        payload={},
        status=EventStatus.FAILED.value,
        error_message="Previous error"
    )
    
    event.reset_for_retry()
    
    assert event.status == EventStatus.PENDING.value
    assert event.error_message is None


def test_event_is_retriable():
    """Test checking if event is retriable."""
    event = Event(
        tenant_id=1,
        event_type=EventType.ORDER_CREATED.value,
        entity_type=EntityType.ORDER.value,
        entity_id="12345",
        idempotency_key="test-key-123",
        payload={}
    )
    
    assert event.is_retriable() is False  # Pending not retriable
    
    event.status = EventStatus.FAILED.value
    assert event.is_retriable() is True
    
    event.status = EventStatus.DEAD_LETTER.value
    assert event.is_retriable() is False


def test_event_is_terminal():
    """Test checking if event is in terminal state."""
    event = Event(
        tenant_id=1,
        event_type=EventType.ORDER_CREATED.value,
        entity_type=EntityType.ORDER.value,
        entity_id="12345",
        idempotency_key="test-key-123",
        payload={}
    )
    
    assert event.is_terminal() is False
    
    event.status = EventStatus.COMPLETED.value
    assert event.is_terminal() is True
    
    event.status = EventStatus.DEAD_LETTER.value
    assert event.is_terminal() is True


def test_event_get_processing_duration():
    """Test calculating processing duration."""
    now = datetime.utcnow()
    event = Event(
        tenant_id=1,
        event_type=EventType.ORDER_CREATED.value,
        entity_type=EntityType.ORDER.value,
        entity_id="12345",
        idempotency_key="test-key-123",
        payload={},
        received_at=now
    )
    
    # Not yet processed
    assert event.get_processing_duration_seconds() is None
    
    # Simulate processing took 5 seconds
    event.processed_at = now + timedelta(seconds=5)
    duration = event.get_processing_duration_seconds()
    
    assert duration == pytest.approx(5.0, abs=0.1)


def test_event_repr():
    """Test string representation."""
    event = Event(
        id=123,
        tenant_id=1,
        event_type=EventType.ORDER_CREATED.value,
        entity_type=EntityType.ORDER.value,
        entity_id="12345",
        idempotency_key="test-key",
        payload={},
        status=EventStatus.PENDING.value
    )
    
    repr_str = repr(event)
    assert "Event" in repr_str
    assert "123" in repr_str
    assert "ORDER_CREATED" in repr_str or "orders/create" in repr_str   