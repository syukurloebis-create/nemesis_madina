"""
NEMESIS Madina - In-Memory Event Dispatcher
Infrastructure implementation of IEventDispatcher.

Enterprise Pattern:
- subscribe/unsubscribe/clear/handlers = Synchronous (registry mutation only)
- publish/publish_many = Asynchronous (handlers may do I/O)
- No locks needed for in-memory registry (Python GIL protects dict operations)
- Snapshot handlers before publishing to avoid mutation during iteration
"""

import asyncio
import logging
from typing import Type, Iterable, Sequence, Callable, Awaitable, Any, Dict, List, Tuple

from backend.domain.events.base import DomainEvent
from backend.domain.events.dispatcher import IEventDispatcher, EventHandler


logger = logging.getLogger(__name__)


class InMemoryEventDispatcher(IEventDispatcher):
    """
    In-Memory Event Dispatcher.

    Characteristics:
    - Synchronous registration (subscribe/unsubscribe/clear)
    - Asynchronous publishing (publish/publish_many)
    - No locks needed (Python GIL protects dict operations)
    - Handler snapshot to prevent mutation during iteration
    - Error isolation (handlers don't break each other)
    """
    
    def __init__(self):
        self._subscribers: Dict[Type[DomainEvent[Any]], List[EventHandler]] = {}
    
    # ============================================================
    # ASYNC PUBLISHING
    # ============================================================
    
    async def publish(self, event: DomainEvent[Any]) -> None:
        """
        Publish a single event to all subscribers.
        ✅ Snapshot handlers before execution to prevent mutation during iteration.
        """
        event_type = type(event)
        # ✅ Snapshot: tuple prevents mutation during iteration
        handlers = tuple(self._subscribers.get(event_type, []))
        
        if not handlers:
            logger.debug(f"No subscribers for {event.event_name}")
            return
        
        logger.debug(f"Publishing {event.event_name} to {len(handlers)} subscribers")
        
        # Execute handlers in parallel with error isolation
        tasks = [
            self._safe_call(handler, event, idx)
            for idx, handler in enumerate(handlers)
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def publish_many(self, events: Iterable[DomainEvent[Any]]) -> None:
        """Publish multiple events sequentially."""
        for event in events:
            await self.publish(event)
    
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
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
            logger.debug(f"Subscribed to {event_type.__name__}")
        else:
            logger.debug(f"Handler already subscribed to {event_type.__name__}")
    
    def unsubscribe(
        self,
        event_type: Type[DomainEvent[Any]],
        handler: EventHandler,
    ) -> None:
        """
        Unsubscribe a handler from an event type.
        ✅ Synchronous - registry mutation only, no I/O.
        """
        if event_type in self._subscribers:
            handlers = self._subscribers[event_type]
            if handler in handlers:
                handlers.remove(handler)
                logger.debug(f"Unsubscribed from {event_type.__name__}")
    
    def clear(self) -> None:
        """
        Clear all subscriptions.
        ✅ Synchronous - registry mutation only, no I/O.
        """
        self._subscribers.clear()
        logger.debug("Cleared all subscriptions")
    
    def handlers(
        self,
        event_type: Type[DomainEvent[Any]],
    ) -> Sequence[EventHandler]:
        """
        Get all handlers for an event type.
        ✅ Returns tuple to prevent external mutation of internal registry.
        """
        return tuple(self._subscribers.get(event_type, []))
    
    # ============================================================
    # HELPERS
    # ============================================================
    
    async def _safe_call(
        self,
        handler: EventHandler,
        event: DomainEvent[Any],
        handler_index: int = 0,
    ) -> None:
        """Call handler with error isolation."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(
                f"Handler {handler_index} failed for {event.event_name}: {e}",
                exc_info=True
            )
            # Don't re-raise - isolate errors
    
    def __len__(self) -> int:
        """Get total number of subscribers."""
        return sum(len(handlers) for handlers in self._subscribers.values())
    
    def __repr__(self) -> str:
        return f"<InMemoryEventDispatcher subscribers={len(self)}>"