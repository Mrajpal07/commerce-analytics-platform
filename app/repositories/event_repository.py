from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Event
from app.repositories.base_repository import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self, db: Session):
        super().__init__(Event, db)
    
    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Event]:
        return self.db.query(Event).filter(
            Event.idempotency_key == idempotency_key
        ).first()
    
    def get_pending_events(self, limit: int = 100) -> List[Event]:
        return self.db.query(Event).filter(
            Event.status == "pending"
        ).order_by(Event.received_at).limit(limit).all()
    
    def get_failed_retriable_events(self, max_retries: int = 5) -> List[Event]:
        return self.db.query(Event).filter(
            and_(
                Event.status == "failed",
                Event.retry_count < max_retries
            )
        ).order_by(Event.received_at).all()