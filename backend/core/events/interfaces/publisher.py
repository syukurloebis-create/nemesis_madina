"""
Event Publisher Interface
=========================

Defines the IEventPublisher interface for publishing events.

ADR Reference: ADR-033
Requirements: REQ-PUB-001, REQ-PUB-002
"""

from abc import ABC, abstractmethod
from typing import Optional

from backend.core.events.interfaces.event import IEvent


class IEventPublisher(ABC):
    """
    Event Publisher Contract.

    Publishes events to all registered subscribers.
    Best-effort delivery: subscriber errors are isolated.

    Semantics (ADR-032):
    - Publish: Emit domain event to all subscribers
    - Intent: Notify, not control
    - Guarantee: Best-effort delivery
    - Error: Subscriber errors are isolated
    - Order: No ordering guarantee
    """

    @abstractmethod
    async def publish(self, event: IEvent) -> None:
        """
        Publish an event to all registered subscribers.

        Precondition: event is not None
        Precondition: event.event_type is not empty
        Postcondition: Publish operation accepted
        Postcondition: Subscribers become eligible

        Args:
            event: The event to publish (must implement IEvent)

        Raises:
            ValueError: If event is None or event_type is empty
        """
        pass

    @abstractmethod
    async def publish_with_correlation(
        self,
        event: IEvent,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Publish an event with correlation ID for tracing.

        Args:
            event: The event to publish
            correlation_id: Optional correlation ID for tracing
        """
        pass