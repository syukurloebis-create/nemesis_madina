"""
Dispatcher Adapter
==================

Wraps the existing IEventDispatcher to conform to canonical interfaces.

ADR Reference: ADR-034
"""

import logging
from typing import Optional

from backend.core.events.interfaces import IEvent

try:
    from backend.domain.events.dispatcher import IEventDispatcher
except ImportError as e:
    raise ImportError(
        "IEventDispatcher not found. Ensure backend.domain.events.dispatcher exists."
    ) from e

logger = logging.getLogger(__name__)


class IDispatcherAdapter:
    """
    Contract for dispatcher adapters.
    """
    async def dispatch(self, event: IEvent) -> None:
        """Dispatch an event."""
        pass


class DispatcherAdapter(IDispatcherAdapter):
    """
    Adapter for the existing IEventDispatcher.

    Transforms the existing API to work with canonical events.
    Does NOT change semantics — only API transformation.
    """

    def __init__(self, dispatcher: Optional[IEventDispatcher] = None):
        """
        Initialize the adapter.

        Args:
            dispatcher: The existing IEventDispatcher instance.
        """
        if dispatcher is None:
            raise ValueError("IEventDispatcher instance required. Use dependency injection.")

        self._dispatcher = dispatcher
        logger.info("DispatcherAdapter initialized")

    async def dispatch(self, event: IEvent) -> None:
        """
        Dispatch an event using the underlying dispatcher.

        Args:
            event: The event to dispatch

        Raises:
            ValueError: If event is None
        """
        if event is None:
            raise ValueError("Event cannot be None")
        if not event.event_type:
            raise ValueError("event_type cannot be empty")

        logger.debug(f"Dispatching event: {event.event_type} (id={event.event_id})")
        await self._dispatcher.dispatch(event)

    @property
    def underlying_dispatcher(self):
        """Get the underlying dispatcher."""
        return self._dispatcher