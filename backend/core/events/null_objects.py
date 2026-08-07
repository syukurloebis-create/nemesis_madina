"""
Null Objects for Optional Dependencies
======================================

Provides null implementations for all optional dependencies.

ADR Reference: ADR-035
"""

import logging
from typing import Optional, Any

from backend.core.events.interfaces import (
    IEvent,
    IEventRouter,
    IEventRetryPolicy,
    IDeadLetterStore,
    Job,
    RoutingDecision,
    RoutingDestination,
    RetryDecision,
    FailureClassification,
    DeadLetterEntry,
)
from backend.core.events.interfaces.subscriber import EventHandler

logger = logging.getLogger(__name__)


class NullEventRouter(IEventRouter):
    """
    Null implementation of IEventRouter.

    Always returns the default destination.
    """

    def route(self, job: Job) -> RoutingDecision:
        """Return default destination."""
        logger.debug("NullEventRouter: routing to default")
        return RoutingDecision(RoutingDestination.IMMEDIATE)

    def get_default_destination(self) -> RoutingDestination:
        """Return immediate as default."""
        return RoutingDestination.IMMEDIATE


class NullEventRetryPolicy(IEventRetryPolicy):
    """
    Null implementation of IEventRetryPolicy.

    Never retries failed events.
    """

    def evaluate(
        self,
        event: IEvent,
        attempt: int,
        failure: Exception,
    ) -> RetryDecision:
        """Never retry."""
        logger.debug(f"NullEventRetryPolicy: aborting retry for {event.event_id}")
        return RetryDecision.abort("Null policy: no retry")

    def classify_failure(self, failure: Exception) -> FailureClassification:
        """Classify as permanent."""
        return FailureClassification.PERMANENT

    def get_max_attempts(self) -> int:
        """No retry attempts."""
        return 0


class NullDeadLetterStore(IDeadLetterStore):
    """
    Null implementation of IDeadLetterStore.

    Does not store any events. Logs warnings.
    """

    def store(self, entry: DeadLetterEntry) -> None:
        """Log warning instead of storing."""
        logger.warning(
            f"NullDeadLetterStore: event {entry.event.event_id} not stored "
            f"(reason: {entry.failure_reason})"
        )

    def get_all(self) -> list[DeadLetterEntry]:
        """Return empty list."""
        return []

    def get_by_event_id(self, event_id: str) -> Optional[DeadLetterEntry]:
        """Return None."""
        return None

    def replay(self, event_id: str) -> bool:
        """Return False."""
        logger.warning(f"NullDeadLetterStore: replay not supported for {event_id}")
        return False

    def remove(self, event_id: str) -> bool:
        """Return False."""
        return False

    def count(self) -> int:
        """Return 0."""
        return 0