"""
Event Bus — Interface + Implementations.

FIX: Dead letter store properly connected.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Awaitable, Optional, Any
import asyncio
import logging

from backend.core.events.interfaces.event import BaseEvent, IEvent
from backend.core.events.interfaces.retry import IEventRetryPolicy, RetryDecision
from backend.core.events.interfaces.dead_letter import DeadLetterEntry, IDeadLetterStore


logger = logging.getLogger(__name__)


class IEventBus(ABC):
    @abstractmethod
    async def publish(self, event: BaseEvent) -> None:
        pass

    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[[BaseEvent], Awaitable[None]]) -> "IEventBus":
        pass


class InMemoryEventBus(IEventBus):
    """
    In-Memory Event Bus with Retry and Dead Letter support.
    """

    def __init__(
        self,
        retry_policy: Optional[IEventRetryPolicy] = None,
        dead_letter_store: Optional[IDeadLetterStore] = None,
    ):
        self._subscribers: Dict[str, List[Callable[[BaseEvent], Awaitable[None]]]] = {}
        self._retry_policy = retry_policy
        self._dead_letter_store = dead_letter_store
        logger.info(f"InMemoryEventBus initialized (retry={retry_policy is not None}, dlq={dead_letter_store is not None})")

    def subscribe(self, event_type: str, handler: Callable[[BaseEvent], Awaitable[None]]) -> "IEventBus":
        if not event_type:
            raise ValueError("event_type cannot be empty")
        if not callable(handler):
            raise ValueError("handler must be callable")

        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

        logger.debug(f"Subscribed to {event_type} (total: {len(self._subscribers[event_type])})")
        return self

    async def publish(self, event: BaseEvent) -> None:
        """Publish an event to all subscribers with retry support."""
        event_type = getattr(event, 'event_type', event.__class__.__name__)
        subscribers = self._subscribers.get(event_type, [])

        if not subscribers:
            logger.debug(f"No subscribers for {event_type}")
            return

        logger.debug(f"Publishing {event_type} to {len(subscribers)} subscribers")

        # Execute each handler with retry support
        tasks = []
        for handler in subscribers:
            tasks.append(self._execute_with_retry(handler, event))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_with_retry(self, handler: Callable, event: BaseEvent) -> None:
        """
        Execute a handler with retry and dead letter support.
        """
        attempt = 0

        while True:
            try:
                await handler(event)
                logger.debug(f"Handler executed successfully for {event.event_type}")
                return

            except Exception as e:
                attempt += 1
                logger.warning(
                    f"Handler failed for {event.event_type} "
                    f"(attempt {attempt}, error: {e})"
                )

                # Check if we should retry
                retry_decision = self._get_retry_decision(event, attempt - 1, e)

                if not retry_decision.should_retry:
                    # Permanent failure — store in dead letter
                    logger.warning(
                        f"Handler permanently failed for {event.event_type} "
                        f"after {attempt} attempts: {retry_decision.reason}"
                    )
                    await self._store_dead_letter(event, e, attempt, retry_decision)
                    return

                # Wait before retry
                delay_seconds = retry_decision.delay_ms / 1000.0
                logger.debug(f"Retrying {event.event_type} in {delay_seconds}s")
                await asyncio.sleep(delay_seconds)

    def _get_retry_decision(self, event: BaseEvent, attempt: int, failure: Exception) -> RetryDecision:
        """Get retry decision from policy or return default."""
        if self._retry_policy is not None:
            return self._retry_policy.evaluate(event, attempt, failure)

        # No retry policy — abort after first failure
        return RetryDecision.abort("No retry policy configured")

    async def _store_dead_letter(
        self,
        event: BaseEvent,
        failure: Exception,
        attempts: int,
        retry_decision: Optional[RetryDecision] = None,
    ) -> None:
        """Store failed event in dead letter store."""
        logger.info(f"_store_dead_letter called: store={self._dead_letter_store is not None}")
        
        if self._dead_letter_store is not None:
            reason = str(failure)
            if retry_decision is not None and retry_decision.reason:
                reason = f"{retry_decision.reason}: {reason}"

            entry = DeadLetterEntry(
                event=event,
                failure_reason=reason,
                failure_type=failure.__class__.__name__,
                attempts=attempts,
            )
            self._dead_letter_store.store(entry)
            logger.info(f"Stored {event.event_type} in dead letter (attempts: {attempts})")
        else:
            logger.warning(
                f"No dead letter store configured — {event.event_type} "
                f"permanently failed after {attempts} attempts"
            )

    def get_handlers(self, event_type: str) -> List[Callable[[BaseEvent], Awaitable[None]]]:
        return self._subscribers.get(event_type, []).copy()

    def set_retry_policy(self, policy: IEventRetryPolicy) -> None:
        """Set the retry policy."""
        self._retry_policy = policy
        logger.info("Retry policy set")

    def set_dead_letter_store(self, store: IDeadLetterStore) -> None:
        """Set the dead letter store."""
        self._dead_letter_store = store
        logger.info("Dead letter store set")

    @property
    def dead_letter_store(self) -> Optional[IDeadLetterStore]:
        """Get the dead letter store."""
        return self._dead_letter_store
