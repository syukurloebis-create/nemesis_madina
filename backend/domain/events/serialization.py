"""
NEMESIS Madina - Event Serialization
"""

import json
from typing import Any, Dict, Type, TypeVar, Optional, Callable
from dataclasses import is_dataclass

from backend.domain.events.base import DomainEvent
from backend.domain.events.metadata import EventMetadata


TEvent = TypeVar('TEvent', bound=DomainEvent)

# Registry for mapping event names to event classes
_EVENT_REGISTRY: Dict[str, Type[DomainEvent]] = {}


class DuplicateEventRegistrationError(Exception):
    """Raised when an event is registered with a duplicate name."""
    pass


class UnknownEventError(Exception):
    """Raised when deserializing an unknown event."""
    pass


class EventVersionMismatchError(Exception):
    """Raised when deserializing an event with mismatched version."""
    pass


def register_event(event_class: Type[DomainEvent]) -> Type[DomainEvent]:
    """
    Decorator to register an event class by its EVENT_NAME.
    Raises DuplicateEventRegistrationError if name already registered.
    """
    if not hasattr(event_class, "EVENT_NAME") or not event_class.EVENT_NAME:
        raise ValueError(
            f"Event class {event_class.__name__} missing EVENT_NAME class variable"
        )
    
    event_name = event_class.EVENT_NAME
    
    if event_name in _EVENT_REGISTRY:
        existing = _EVENT_REGISTRY[event_name]
        raise DuplicateEventRegistrationError(
            f"Duplicate event registration: '{event_name}' already registered by {existing.__name__}"
        )
    
    _EVENT_REGISTRY[event_name] = event_class
    return event_class


def get_event_class(event_name: str) -> Optional[Type[DomainEvent]]:
    """Get event class by event name."""
    return _EVENT_REGISTRY.get(event_name)


def serialize(event: DomainEvent[Any]) -> str:
    """Serialize a domain event to JSON string."""
    return json.dumps(event.to_dict(), default=str)


def deserialize(data: str) -> DomainEvent[Any]:
    """
    Deserialize a domain event from JSON string using registry.
    
    Args:
        data: JSON string
        
    Returns:
        DomainEvent instance
        
    Raises:
        UnknownEventError: If event name not registered
        EventVersionMismatchError: If version doesn't match
    """
    raw = json.loads(data)
    return _dict_to_event(raw)


def _dict_to_event(data: Dict[str, Any]) -> DomainEvent[Any]:
    """Convert dict to domain event using registry."""
    metadata = EventMetadata.from_dict(data["metadata"])
    event_name = data.get("event_name", "UnknownEvent")
    event_version = data.get("event_version", "1")
    
    event_class = get_event_class(event_name)
    if not event_class:
        raise UnknownEventError(f"Unknown event type: '{event_name}'")
    
    # Version validation
    if event_class.EVENT_VERSION != event_version:
        # In the future, we can support version migration here
        # For now, exact match required
        raise EventVersionMismatchError(
            f"Event version mismatch: '{event_name}' version {event_version} "
            f"expected {event_class.EVENT_VERSION}"
        )
    
    # Get payload type from event class
    payload_type = event_class.__dataclass_fields__["payload"].type
    payload = _dict_to_payload(data["payload"], payload_type)
    
    return event_class(metadata=metadata, payload=payload)


def _dict_to_payload(data: Dict[str, Any], payload_class: Type) -> Any:
    """Convert dict to payload instance."""
    if hasattr(payload_class, "from_dict"):
        return payload_class.from_dict(data)
    
    if is_dataclass(payload_class):
        try:
            return payload_class(**data)
        except TypeError:
            return data
    
    return data