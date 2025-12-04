"""
Event Model

Represents events in the event store (append-only log).
Core component of event-driven architecture.

Enforces:
- INV-2: Event Idempotency (unique idempotency_key)
- INV-5: Auditability (complete payload storage)
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    Index,
    CheckConstraint,
    JSON,
)
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base, BaseModel, TenantMixin


class EventStatus(str, Enum):
    """
    Event processing status.
    
    State transitions:
        pending → processing → completed
        pending → processing → failed (retry_count < max) → pending
        pending → processing → failed (retry_count >= max) → dead_letter
    """
    PENDING = "pending"          # Waiting to be processed
    PROCESSING = "processing"     # Currently being processed
    COMPLETED = "completed"       # Successfully processed
    FAILED = "failed"            # Processing failed (will retry)
    DEAD_LETTER = "dead_letter"  # Permanently failed after max retries


class EventType(str, Enum):
    """
    Supported event types.
    
    Primarily Shopify webhook events, but extensible for other sources.
    """
    # Order events
    ORDER_CREATED = "orders/create"
    ORDER_UPDATED = "orders/updated"
    ORDER_CANCELLED = "orders/cancelled"
    ORDER_FULFILLED = "orders/fulfilled"
    ORDER_PAID = "orders/paid"
    
    # Customer events
    CUSTOMER_CREATED = "customers/create"
    CUSTOMER_UPDATED = "customers/update"
    CUSTOMER_DELETED = "customers/delete"
    
    # Product events
    PRODUCT_CREATED = "products/create"
    PRODUCT_UPDATED = "products/update"
    PRODUCT_DELETED = "products/delete"
    
    # Manual sync events
    MANUAL_SYNC_REQUESTED = "sync/requested"
    RECONCILIATION_STARTED = "reconciliation/started"


class EntityType(str, Enum):
    """Entity types that events can reference."""
    ORDER = "order"
    CUSTOMER = "customer"
    PRODUCT = "product"
    LINE_ITEM = "line_item"
    TENANT = "tenant"


class Event(BaseModel, TenantMixin, Base):
    """
    Event Store Model
    
    Immutable append-only log of all system events.
    Each event represents a state change in an external system (Shopify)
    or an internal command (manual sync).
    
    Attributes:
        event_type: Type of event (e.g., "orders/create")
        entity_type: Type of entity affected (e.g., "order")
        entity_id: External ID of the entity (e.g., Shopify order ID)
        idempotency_key: Unique key to prevent duplicate processing
        payload: Full event data (JSONB)
        status: Current processing status
        received_at: When event was received
        processed_at: When processing completed/failed
        retry_count: Number of retry attempts
        error_message: Error details if processing failed
        correlation_id: For distributed tracing
    """
    
    __tablename__ = "events"
    
    # ========================================================================
    # EVENT IDENTIFICATION
    # ========================================================================
    
    event_type = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Event type (e.g., 'orders/create')"
    )
    
    entity_type = Column(
        String(50),
        nullable=False,
        index=True,
        doc="Type of entity this event affects"
    )
    
    entity_id = Column(
        String(255),
        nullable=False,
        index=True,
        doc="External ID of the entity (e.g., Shopify order ID)"
    )
    
    idempotency_key = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Unique key to prevent duplicate processing (INV-2)"
    )
    
    # ========================================================================
    # EVENT DATA
    # ========================================================================
    
    payload = Column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        doc="Complete event data (INV-5: Auditability)"
    )
    
    # ========================================================================
    # PROCESSING STATE
    # ========================================================================
    
    status = Column(
        String(50),
        nullable=False,
        default=EventStatus.PENDING.value,
        index=True,
        doc="Current processing status"
    )
    
    received_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
        doc="When event was received by our system"
    )
    
    processed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When processing completed (success or final failure)"
    )
    
    retry_count = Column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of processing attempts"
    )
    
    error_message = Column(
        Text,
        nullable=True,
        doc="Error details if processing failed"
    )
    
    # ========================================================================
    # OBSERVABILITY
    # ========================================================================
    
    correlation_id = Column(
        String(255),
        nullable=True,
        index=True,
        doc="Correlation ID for distributed tracing"
    )


    # ========================================================================
    # INITIALIZATION
    # ========================================================================
    
    def __init__(self, **kwargs):
        """
        Initialize Event with default values.
        
        Ensures defaults are set even when creating objects in memory
        (not just when inserting into database).
        """
        # Set defaults if not provided
        if 'status' not in kwargs:
            kwargs['status'] = EventStatus.PENDING.value
        
        if 'retry_count' not in kwargs:
            kwargs['retry_count'] = 0
        
        if 'received_at' not in kwargs:
            kwargs['received_at'] = datetime.utcnow()
        
        # Call parent constructor
        super().__init__(**kwargs)
    

    
    # ========================================================================
    # TABLE CONSTRAINTS & INDEXES
    # ========================================================================
    
    __table_args__ = (
        # Composite index for tenant + status queries
        Index(
            "ix_events_tenant_status",
            "tenant_id",
            "status"
        ),
        
        # Composite index for tenant + entity queries
        Index(
            "ix_events_tenant_entity",
            "tenant_id",
            "entity_type",
            "entity_id"
        ),
        
        # Index for processing queue (pending events, oldest first)
        Index(
            "ix_events_processing_queue",
            "status",
            "received_at"
        ),
        
        # Check constraint for valid status
        CheckConstraint(
            f"status IN ('{EventStatus.PENDING.value}', '{EventStatus.PROCESSING.value}', "
            f"'{EventStatus.COMPLETED.value}', '{EventStatus.FAILED.value}', '{EventStatus.DEAD_LETTER.value}')",
            name="check_event_status"
        ),
        
        # Check constraint for non-negative retry count
        CheckConstraint(
            "retry_count >= 0",
            name="check_retry_count_positive"
        ),
    )
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def mark_as_processing(self) -> None:
        """Mark event as currently being processed."""
        self.status = EventStatus.PROCESSING.value
    
    def mark_as_completed(self) -> None:
        """Mark event as successfully processed."""
        self.status = EventStatus.COMPLETED.value
        self.processed_at = datetime.utcnow()
    
    def mark_as_failed(self, error_message: str, max_retries: int = 5) -> None:
        """
        Mark event as failed and increment retry count.
        
        Args:
            error_message: Error details
            max_retries: Maximum retry attempts before dead letter
        """
        self.retry_count += 1
        self.error_message = error_message
        
        if self.retry_count >= max_retries:
            self.status = EventStatus.DEAD_LETTER.value
            self.processed_at = datetime.utcnow()
        else:
            self.status = EventStatus.FAILED.value
    
    def reset_for_retry(self) -> None:
        """Reset event to pending status for retry."""
        if self.status == EventStatus.FAILED.value:
            self.status = EventStatus.PENDING.value
            self.error_message = None
    
    def is_retriable(self) -> bool:
        """Check if event can be retried."""
        return self.status == EventStatus.FAILED.value
    
    def is_terminal(self) -> bool:
        """Check if event is in a terminal state (completed or dead letter)."""
        return self.status in [EventStatus.COMPLETED.value, EventStatus.DEAD_LETTER.value]
    
    def get_processing_duration_seconds(self) -> Optional[float]:
        """
        Calculate processing duration in seconds.
        
        Returns:
            float: Duration in seconds, or None if not yet processed
        """
        if self.processed_at is None:
            return None
        
        return (self.processed_at - self.received_at).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary (override base method to handle JSONB).
        
        Returns:
            Dict representation of event
        """
        result = super().to_dict()
        
        # payload is already a dict (JSONB)
        # No need to parse it
        
        return result
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Event(id={self.id}, tenant_id={self.tenant_id}, "
            f"type={self.event_type}, entity={self.entity_type}:{self.entity_id}, "
            f"status={self.status})>"
        )