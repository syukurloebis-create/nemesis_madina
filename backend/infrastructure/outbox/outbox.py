# backend/infrastructure/outbox/outbox.py
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import uuid

class OutboxStatus(Enum):
    """Status of outbox message"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"

@dataclass
class OutboxMessage:
    """Outbox message entity"""
    id: str
    event_id: str
    event_type: str
    payload: dict
    status: OutboxStatus
    created_at: datetime
    processed_at: Optional[datetime] = None
    retry_count: int = 0
    error_message: Optional[str] = None

class OutboxRepository:
    """Repository for outbox messages"""
    
    def __init__(self, session):
        self.session = session
    
    async def save(self, message: OutboxMessage):
        """Save outbox message"""
        # Implementation depends on storage
        pass
    
    async def get_pending(self, limit: int = 100) -> List[OutboxMessage]:
        """Get pending messages"""
        # Implementation depends on storage
        return []
    
    async def mark_completed(self, message_id: str):
        """Mark message as completed"""
        pass
    
    async def mark_failed(self, message_id: str, error: str):
        """Mark message as failed"""
        pass
    
    async def retry(self, message_id: str):
        """Retry a failed message"""
        pass