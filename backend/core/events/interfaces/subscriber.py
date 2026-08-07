"""
Event Subscriber Interface
==========================

Defines the IEventSubscriber interface for subscribing to events.

ADR Reference: ADR-033
Requirements: REQ-SUB-001
"""

from abc import ABC, abstractmethod
from typing import Callable, Awaitable

from backend.core.events.interfaces.event import IEvent


EventHandler = Callable[[IEvent], Awaitable[None]]


class IEventSubscriber(ABC):
    """
    Event Subscriber Contract.

    Registers handlers for specific event types.

    Semantics (ADR-032):
    - Subscribe: Register a handler for a specific event type
    - Handler: Async function accepting event
    - Duplicate: Same handler registered twice = no effect
    """

    @abstractmethod
    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        """
        Register a handler for an event type.

        Precondition: event_type is not empty
        Precondition: handler is callable
        Postcondition: handler is registered
        Postcondition: duplicate registration is idempotent

        Args:
            event_type: The type of event to subscribe to
            handler: Async function that processes the event

        Raises:
            ValueError: If event_type is empty or handler is not callable
        """
        pass

    @abstractmethod
    def unsubscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        """
        Unregister a handler for an event type.

        Args:
            event_type: The type of event to unsubscribe from
            handler: The handler to remove
        """
        pass

    @abstractmethod
    def get_handlers(self, event_type: str) -> list[EventHandler]:
        """
        Get all handlers registered for an event type.

        Args:
            event_type: The event type to query

        Returns:
            List of registered handlers
        """
        pass