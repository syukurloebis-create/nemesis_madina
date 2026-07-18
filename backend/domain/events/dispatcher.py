"""
NEMESIS Madina - Event Dispatcher Contract
"""

from typing import Protocol, Type, Iterable, Sequence, Callable, Awaitable, Any, runtime_checkable
from backend.domain.events.base import DomainEvent


EventHandler = Callable[[DomainEvent[Any]], Awaitable[None]]


@runtime_checkable
class IEventDispatcher(Protocol):
    """
    Event Dispatcher Contract - Domain Layer.
    
    Enterprise Pattern:
    - subscribe/unsubscribe/clear/handlers = Synchronous (registry mutation only)
    - publish/publish_many = Asynchronous (handlers may do I/O)
    """
    
    # ============================================================
    # ASYNC PUBLISHING
    # ============================================================
    
    async def publish(self, event: DomainEvent[Any]) -> None:
        """
        Publish a single event to all subscribers.
        
        Args:
            event: The domain event to publish
            
        Raises:
            EventHandlerError: If a handler fails (isolated)
        """
        ...
    
    async def publish_many(self, events: Iterable[DomainEvent[Any]]) -> None:
        """
        Publish multiple events to all subscribers.
        
        Args:
            events: Iterable of domain events to publish
        """
        ...
    
    # ============================================================
    # SYNC REGISTRATION
    # ============================================================
    
    def subscribe(
        self,
        event_type: Type[DomainEvent[Any]],
        handler: EventHandler,
    ) -> None:
        """
        Subscribe a handler to an event type.
        ✅ Synchronous - registry mutation only, no I/O.
        
        Args:
            event_type: The event class to subscribe to
            handler: Async function to handle the event
        """
        ...
    
    def unsubscribe(
        self,
        event_type: Type[DomainEvent[Any]],
        handler: EventHandler,
    ) -> None:
        """
        Unsubscribe a handler from an event type.
        ✅ Synchronous - registry mutation only, no I/O.
        
        Args:
            event_type: The event class to unsubscribe from
            handler: The handler to remove
        """
        ...
    
    def clear(self) -> None:
        """
        Clear all subscriptions.
        ✅ Synchronous - registry mutation only, no I/O.
        """
        ...
    
    def handlers(
        self,
        event_type: Type[DomainEvent[Any]],
    ) -> Sequence[EventHandler]:
        """
        Get all handlers for an event type.
        ✅ Synchronous - registry read only, no I/O.
        
        Args:
            event_type: The event class to get handlers for
            
        Returns:
            Sequence of handlers (tuple)
        """
        ...