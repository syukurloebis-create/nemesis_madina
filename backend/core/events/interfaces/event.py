"""
Canonical Event Contract
========================

Defines the IEvent interface — the canonical event contract.
All domain events MUST implement this interface.

ADR Reference: ADR-032, ADR-033
Requirements: REQ-EVT-001, REQ-EVT-002
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4
from types import MappingProxyType


@dataclass(frozen=True)
class BaseEvent(ABC):
    """
    Base implementation of IEvent.

    Immutable by design using frozen dataclass.
    Payload is wrapped in MappingProxyType for true immutability.
    Timezone-aware UTC timestamps.

    IMPORTANT: Field order matters for dataclass.
    Fields WITHOUT defaults must come BEFORE fields WITH defaults.
    """

    # ===== REQUIRED FIELDS (no defaults) =====
    event_type: str
    _payload: Mapping[str, Any]

    # ===== OPTIONAL FIELDS (with defaults) =====
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        """Validate and freeze payload."""
        # Convert payload to immutable MappingProxyType
        if not isinstance(self._payload, MappingProxyType):
            object.__setattr__(self, "_payload", MappingProxyType(dict(self._payload)))

        # Ensure event_type is not empty
        if not self.event_type:
            raise ValueError("event_type cannot be empty")

        # Ensure occurred_at is timezone-aware
        if self.occurred_at.tzinfo is None:
            object.__setattr__(self, "occurred_at", self.occurred_at.replace(tzinfo=timezone.utc))

    @property
    def payload(self) -> Mapping[str, Any]:
        """Immutable event payload."""
        return self._payload

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "payload": dict(self._payload),
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.event_id}, type={self.event_type})>"


# IEvent is now an alias for BaseEvent for backward compatibility
IEvent = BaseEvent


class DomainEvent(BaseEvent):
    """
    Domain event marker.

    Use this for domain events to distinguish them from infrastructure events.
    """

    def __init__(
        self,
        event_type: str,
        payload: Mapping[str, Any],
        event_id: Optional[str] = None,
        occurred_at: Optional[datetime] = None,
        metadata: Optional[Mapping[str, Any]] = None,  
    ):
        super().__init__(
            event_type=event_type,
            _payload=payload,
            event_id=event_id,
            occurred_at=occurred_at,
        )
        self._metadata = metadata or {}

