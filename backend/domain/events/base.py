"""
NEMESIS Madina - Domain Event Base
Pure domain event - no infrastructure metadata.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar, Any
from datetime import datetime, timezone

TPayload = TypeVar('TPayload')


@dataclass(frozen=True)
class DomainEvent(Generic[TPayload]):
    """
    Pure domain event - no infrastructure coupling.
    
    ✅ No producer, no aggregate_type, no schema_version
    ✅ Only domain-relevant fields
    ✅ Infrastructure adds metadata later
    ✅ Payload pattern for consistency
    """
    
    payload: TPayload
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, "occurred_at", datetime.now(timezone.utc))
    
    @property
    def event_name(self) -> str:
        return self.__class__.__name__
    
    @property
    def payload_dict(self):
        """Convert payload to dict for serialization"""
        if hasattr(self.payload, 'to_dict'):
            return self.payload.to_dict()
        return self.payload