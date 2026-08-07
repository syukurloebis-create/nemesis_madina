"""
Event Bus Facade
================

Unified entry point for all event operations.
Composes all canonical interfaces.

ADR Reference: ADR-035

Rules:
- Contains ZERO business logic
- Only delegates to composed interfaces
- No direct instantiation of dependencies
- Immutable after construction
"""

import logging
from typing import Optional

from backend.core.events.interfaces import (
    IEvent,
    IEventPublisher,
    IEventSubscriber,
    IEventRouter,
    IEventRetryPolicy,
    IDeadLetterStore,
)
from backend.core.events.interfaces.subscriber import EventHandler
from backend.core.events.interfaces.router import Job, RoutingDecision, RoutingDestination
from backend.core.events.interfaces.retry import RetryDecision, FailureClassification
from backend.core.events.interfaces.dead_letter import DeadLetterEntry
from backend.core.events.null_objects import (
    NullEventRouter,
    NullEventRetryPolicy,
    NullDeadLetterStore,
)

logger = logging.getLogger(__name__)


class EventBusFacade:
    """
    Unified entry point for all event operations.

    Composes all canonical interfaces.
    Delegates calls to the composed interfaces.
    Contains ZERO business logic.

    Invariants:
    - publisher, subscriber are required
    - router, retry_policy, dead_letter_store are optional
    - Facade is immutable after construction
    - Null Object Pattern used for all optional dependencies
    """

    def __init__(
        self,
        publisher: IEventPublisher,
        subscriber: IEventSubscriber,
        router: Optional[IEventRouter] = None,
        retry_policy: Optional[IEventRetryPolicy] = None,
        dead_letter_store: Optional[IDeadLetterStore] = None,
        use_null_objects: bool = True,
    ):
        """
        Initialize the facade with all required components.

        Args:
            publisher: The event publisher implementation
            subscriber: The event subscriber implementation
            router: Optional router implementation
            retry_policy: Optional retry policy implementation
            dead_letter_store: Optional dead letter store implementation
            use_null_objects: If True, use null objects for missing dependencies
        """
        if publisher is None:
            raise ValueError("publisher cannot be None")
        if subscriber is None:
            raise ValueError("subscriber cannot be None")

        self._publisher = publisher
        self._subscriber = subscriber

        # Use null objects for optional dependencies if enabled
        if use_null_objects:
            self._router = router or NullEventRouter()
            self._retry_policy = retry_policy or NullEventRetryPolicy()
            self._dead_letter_store = dead_letter_store or NullDeadLetterStore()
        else:
            self._router = router
            self._retry_policy = retry_policy
            self._dead_letter_store = dead_letter_store

        self._use_null_objects = use_null_objects

        logger.info("EventBusFacade initialized")

    # ========== Publish Methods ==========

    async def publish(self, event: IEvent) -> None:
        """Publish an event to all registered subscribers."""
        await self._publisher.publish(event)

    async def publish_with_correlation(
        self,
        event: IEvent,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Publish an event with correlation ID."""
        await self._publisher.publish_with_correlation(event, correlation_id)

    # ========== Subscribe Methods ==========

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Register a handler for an event type."""
        self._subscriber.subscribe(event_type, handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unregister a handler for an event type."""
        self._subscriber.unsubscribe(event_type, handler)

    def get_handlers(self, event_type: str) -> list[EventHandler]:
        """Get all handlers registered for an event type."""
        return self._subscriber.get_handlers(event_type)

    # ========== Router Methods ==========

    def route(self, job: Job) -> RoutingDecision:
        """Route a job to an execution destination."""
        return self._router.route(job)

    def get_default_destination(self) -> RoutingDestination:
        """Get the default routing destination."""
        return self._router.get_default_destination()

    # ========== Retry Methods ==========

    def evaluate_retry(
        self,
        event: IEvent,
        attempt: int,
        failure: Exception,
    ) -> RetryDecision:
        """Evaluate whether to retry a failed event."""
        return self._retry_policy.evaluate(event, attempt, failure)

    def classify_failure(self, failure: Exception) -> FailureClassification:
        """Classify the type of failure."""
        return self._retry_policy.classify_failure(failure)

    def get_max_retries(self) -> int:
        """Get the maximum number of retry attempts."""
        return self._retry_policy.get_max_attempts()

    # ========== Dead Letter Methods ==========

    def store_dead_letter(self, entry: DeadLetterEntry) -> None:
        """Store a failed event in the dead letter store."""
        self._dead_letter_store.store(entry)

    def get_dead_letters(self) -> list[DeadLetterEntry]:
        """Get all dead letter entries."""
        return self._dead_letter_store.get_all()

    def get_dead_letter(self, event_id: str) -> Optional[DeadLetterEntry]:
        """Get a dead letter entry by event ID."""
        return self._dead_letter_store.get_by_event_id(event_id)

    def replay_dead_letter(self, event_id: str) -> bool:
        """Replay a dead letter event."""
        return self._dead_letter_store.replay(event_id)

    def remove_dead_letter(self, event_id: str) -> bool:
        """Remove a dead letter entry."""
        return self._dead_letter_store.remove(event_id)

    def count_dead_letters(self) -> int:
        """Get the total number of dead letter entries."""
        return self._dead_letter_store.count()

    # ========== Accessors ==========

    @property
    def publisher(self) -> IEventPublisher:
        """Get the publisher implementation."""
        return self._publisher

    @property
    def subscriber(self) -> IEventSubscriber:
        """Get the subscriber implementation."""
        return self._subscriber

    @property
    def router(self) -> IEventRouter:
        """Get the router implementation."""
        return self._router

    @property
    def retry_policy(self) -> IEventRetryPolicy:
        """Get the retry policy implementation."""
        return self._retry_policy

    @property
    def dead_letter_store(self) -> IDeadLetterStore:
        """Get the dead letter store implementation."""
        return self._dead_letter_store

    @property
    def has_null_objects(self) -> bool:
        """Check if null objects are being used."""
        return self._use_null_objects