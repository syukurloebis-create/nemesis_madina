"""
NEMESIS Madina - Domain Event Base
Backward compatible event contract.

Supports:
- New payload-based events
- Legacy metadata-based events
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Generic, TypeVar, Any, Mapping, Optional
from uuid import uuid4


TPayload = TypeVar("TPayload")


@dataclass(frozen=True)
class DomainEvent(Generic[TPayload]):

    payload: TPayload = None
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    event_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    # compatibility fields
    event_type: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        payload=None,
        occurred_at=None,
        event_type=None,
        metadata=None,
        event_id=None,
    ):
        object.__setattr__(self, "payload", payload)
        object.__setattr__(
            self,
            "occurred_at",
            occurred_at if occurred_at is not None else datetime.now(timezone.utc)
        )
        object.__setattr__(
            self,
            "event_type",
            event_type if event_type is not None else self.__class__.__name__
        )
        object.__setattr__(
            self,
            "metadata",
            metadata if metadata is not None else {}
        )
        object.__setattr__(
            self,
            "event_id",
            event_id if event_id is not None else str(uuid4())
        )

    @property
    def event_name(self) -> str:
        return self.event_type or self.__class__.__name__

    @property
    def payload_dict(self):
        if hasattr(self.payload, "to_dict"):
            return self.payload.to_dict()
        return self.payload

    def to_dict(self) -> dict:
        """Serialize domain event into JSON-compatible dictionary."""
        # Serialize payload
        payload = self.payload
        if hasattr(payload, "to_dict"):
            payload = payload.to_dict()
        elif hasattr(payload, "__dict__"):
            payload = payload.__dict__

        # Serialize metadata
        metadata = {}
        if hasattr(self.metadata, "to_dict"):
            metadata = self.metadata.to_dict()
        elif hasattr(self.metadata, "__dict__"):
            metadata = self.metadata.__dict__
        elif self.metadata:
            metadata = dict(self.metadata)

        return {
            "event_id": str(self.event_id),
            "event_name": self.event_name,  # ← ADD THIS
            "event_type": self.event_type,
            "payload": payload,
            "metadata": metadata,
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at else None,
        }
