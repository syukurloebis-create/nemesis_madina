"""
Canonical Event Models
======================

Domain event models that implement the IEvent interface.

ADR Reference: ADR-032, ADR-033
"""

from typing import Any, Mapping
from datetime import datetime, timezone

from backend.core.events.interfaces.event import BaseEvent, DomainEvent


class EventFactory:
    """
    Factory for creating domain events.

    Provides a consistent way to create events with validation.
    """

    @staticmethod
    def create(
        event_type: str,
        payload: Mapping[str, Any],
        event_id: str = None,
        occurred_at: datetime = None,
    ) -> DomainEvent:
        """
        Create a new domain event.

        Args:
            event_type: The type of event
            payload: The event payload (will be made immutable)
            event_id: Optional custom event ID
            occurred_at: Optional custom timestamp

        Returns:
            DomainEvent: The created event

        Raises:
            ValueError: If event_type is empty
        """
        if not event_type:
            raise ValueError("event_type cannot be empty")

        return DomainEvent(
            event_type=event_type,
            payload=dict(payload) if payload else {},
            event_id=event_id,
            occurred_at=occurred_at or datetime.now(timezone.utc),
        )


# Convenience alias
create_event = EventFactory.create