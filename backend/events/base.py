# backend/events/base.py
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid

class EventMetadata(BaseModel):
    """Standar metadata untuk semua event"""
    
    # Tracing
    correlation_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    causation_id: Optional[uuid.UUID] = None
    
    # Actor
    actor_id: uuid.UUID
    actor_role: str  # INVESTIGATOR, IRBAN, INSPEKTUR, ADMIN, EXECUTIVE, SYSTEM
    
    # Context
    tenant_id: uuid.UUID
    source_system: str = "NEMESIS_API"  # NEMESIS_API, NEMESIS_WORKER, EXTERNAL_INTEGRATION
    
    # Technical (optional)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BaseEvent(BaseModel):
    """Base class untuk semua event"""
    
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    aggregate_type: str
    aggregate_id: uuid.UUID
    event_type: str
    event_version: int = 1
    payload: Dict[str, Any]
    metadata: EventMetadata
    
    # Hash chain fields
    event_hash: Optional[str] = None
    previous_hash: Optional[str] = None
    
    def compute_hash(self) -> str:
        """Compute SHA256 hash of event content"""
        import hashlib
        import json
        
        content = {
            "event_id": str(self.event_id),
            "aggregate_type": self.aggregate_type,
            "aggregate_id": str(self.aggregate_id),
            "event_type": self.event_type,
            "event_version": self.event_version,
            "payload": self.payload,
            "metadata": {
                "correlation_id": str(self.metadata.correlation_id),
                "causation_id": str(self.metadata.causation_id) if self.metadata.causation_id else None,
                "actor_id": str(self.metadata.actor_id),
                "actor_role": self.metadata.actor_role,
                "tenant_id": str(self.metadata.tenant_id),
                "timestamp": self.metadata.timestamp.isoformat()
            }
        }
        
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()