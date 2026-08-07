"""
Infrastructure EventBus Adapter
===============================

FIX: Adapter now properly passes retry_policy and dead_letter_store to bus.
"""

import logging
from typing import Optional

from backend.core.events.interfaces import IEvent, IEventPublisher, IEventSubscriber
from backend.core.events.interfaces.subscriber import EventHandler
from backend.core.events.interfaces.event import BaseEvent
from backend.core.events.interfaces.retry import IEventRetryPolicy
from backend.core.events.interfaces.dead_letter import IDeadLetterStore
from backend.infrastructure.event_bus import InMemoryEventBus

logger = logging.getLogger(__name__)


class InfrastructureEventBusAdapter(IEventPublisher, IEventSubscriber):
    _shared_bus: Optional[InMemoryEventBus] = None
    _retry_policy: Optional[IEventRetryPolicy] = None
    _dead_letter_store: Optional[IDeadLetterStore] = None

    @classmethod
    def get_shared_bus(cls) -> InMemoryEventBus:
        if cls._shared_bus is None:
            cls._shared_bus = InMemoryEventBus(
                retry_policy=cls._retry_policy,
                dead_letter_store=cls._dead_letter_store,
            )
            logger.info(f"Shared InMemoryEventBus created (dlq={cls._dead_letter_store is not None})")
        return cls._shared_bus

    @classmethod
    def configure(cls, retry_policy: Optional[IEventRetryPolicy] = None,
                  dead_letter_store: Optional[IDeadLetterStore] = None) -> None:
        """Configure shared bus with retry and dead letter."""
        cls._retry_policy = retry_policy
        cls._dead_letter_store = dead_letter_store
        # Reset bus so it picks up new config
        cls._shared_bus = None
        logger.info(f"InfrastructureEventBusAdapter configured (dlq={dead_letter_store is not None})")

    def __init__(self, bus: Optional[InMemoryEventBus] = None,
                 retry_policy: Optional[IEventRetryPolicy] = None,
                 dead_letter_store: Optional[IDeadLetterStore] = None):
        if bus is not None:
            self._bus = bus
        else:
            # Use configured retry and dead letter
            cls = self.__class__
            if retry_policy is not None:
                cls._retry_policy = retry_policy
            if dead_letter_store is not None:
                cls._dead_letter_store = dead_letter_store
            self._bus = self.get_shared_bus()
            logger.info(f"InfrastructureEventBusAdapter initialized (bus dlq={self._bus.dead_letter_store is not None})")

    async def publish(self, event: IEvent) -> None:
        if event is None:
            raise ValueError("Event cannot be None")
        if not event.event_type:
            raise ValueError("event_type cannot be empty")

        logger.debug(f"Publishing event: {event.event_type} (id={event.event_id})")
        await self._bus.publish(event)

    async def publish_with_correlation(
        self,
        event: IEvent,
        correlation_id: Optional[str] = None,
    ) -> None:
        await self.publish(event)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if not event_type:
            raise ValueError("event_type cannot be empty")
        if not callable(handler):
            raise ValueError("handler must be callable")

        logger.debug(f"Subscribing to {event_type}")
        self._bus.subscribe(event_type, handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        logger.warning("Unsubscribe not fully implemented")

    def get_handlers(self, event_type: str) -> list[EventHandler]:
        return []

    @property
    def underlying_bus(self):
        return self._bus

    @classmethod
    def reset_shared_bus(cls):
        cls._shared_bus = None
        cls._retry_policy = None
        cls._dead_letter_store = None
        logger.info("Shared InMemoryEventBus reset")
