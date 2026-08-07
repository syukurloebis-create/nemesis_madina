"""
Event Normalizer
================

Provides event normalization for backward compatibility.

ADR Reference: ADR-036
"""

from typing import Any, Dict, Optional
from backend.core.events.events import EventFactory
from backend.core.events.interfaces import BaseEvent


class EventNormalizer:
    """
    Normalizes events to canonical format.

    This provides backward compatibility for existing code
    that expects events in a specific format.
    """

    @staticmethod
    def normalize(event: Any) -> BaseEvent:
        """
        Normalize an event to canonical format.

        Args:
            event: The event to normalize (can be dict, object, or BaseEvent)

        Returns:
            BaseEvent: The normalized event

        Raises:
            ValueError: If the event cannot be normalized
        """
        if event is None:
            raise ValueError("event cannot be None")

        # Already canonical
        if isinstance(event, BaseEvent):
            return event

        # Dict format
        if isinstance(event, dict):
            event_type = event.get('type') or event.get('event_type', 'unknown')
            payload = event.get('data') or event.get('payload', {})
            return EventFactory.create(
                event_type=event_type,
                payload=payload,
                event_id=event.get('event_id'),
            )

        # Object with attributes
        if hasattr(event, 'type') and hasattr(event, 'data'):
            return EventFactory.create(
                event_type=event.type,
                payload=event.data if event.data else {},
            )

        # Object with __dict__
        if hasattr(event, '__dict__'):
            # Try to extract event info
            data = {k: v for k, v in event.__dict__.items() if not k.startswith('_')}
            return EventFactory.create(
                event_type=event.__class__.__name__,
                payload=data,
            )

        raise ValueError(f"Cannot normalize event of type {type(event)}")

    @staticmethod
    def normalize_payload(payload: Any) -> Dict[str, Any]:
        """
        Normalize a payload to dictionary format.

        Args:
            payload: The payload to normalize

        Returns:
            Dict: The normalized payload
        """
        if payload is None:
            return {}

        if isinstance(payload, dict):
            return payload

        if hasattr(payload, 'to_dict'):
            return payload.to_dict()

        if hasattr(payload, '__dict__'):
            return {k: v for k, v in payload.__dict__.items() if not k.startswith('_')}

        return {"value": payload}