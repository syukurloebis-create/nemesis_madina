"""
Default Retry Policy
====================

Default implementation of IEventRetryPolicy.

ADR Reference: ADR-033
Requirements: REQ-RET-001
"""

import logging
import random
from typing import Optional

from backend.core.events.interfaces.retry import (
    IEventRetryPolicy,
    RetryDecision,
    FailureClassification,
)
from backend.core.events.interfaces.event import IEvent

logger = logging.getLogger(__name__)


class DefaultRetryPolicy(IEventRetryPolicy):
    """
    Default implementation of IEventRetryPolicy.

    Features:
    - Configurable max attempts (default: 3)
    - Fixed delay between retries (default: 100ms)
    - Classifies failures as recoverable or permanent
    - Deterministic decisions
    """

    def __init__(
        self,
        max_attempts: int = 3,
        delay_ms: int = 100,
        recoverable_exceptions: Optional[list[type[Exception]]] = None,
    ):
        """
        Initialize the default retry policy.

        Args:
            max_attempts: Maximum number of retry attempts
            delay_ms: Delay between retries in milliseconds
            recoverable_exceptions: List of exception types considered recoverable
        """
        self._max_attempts = max_attempts
        self._delay_ms = delay_ms
        self._recoverable_exceptions = recoverable_exceptions or [
            ConnectionError,
            TimeoutError,
            OSError,
        ]
        logger.info(f"DefaultRetryPolicy initialized (max={max_attempts}, delay={delay_ms}ms)")

    def evaluate(
        self,
        event: IEvent,
        attempt: int,
        failure: Exception,
    ) -> RetryDecision:
        """
        Evaluate whether to retry a failed event.

        Args:
            event: The event that failed
            attempt: The current attempt number (0-based)
            failure: The exception that occurred

        Returns:
            RetryDecision: Whether to retry and with what delay
        """
        if event is None:
            raise ValueError("event cannot be None")

        if attempt < 0:
            raise ValueError("attempt must be >= 0")

        classification = self.classify_failure(failure)

        # Permanent failures should not be retried
        if classification in (FailureClassification.PERMANENT, FailureClassification.PROGRAMMING):
            logger.debug(f"Event {event.event_id}: permanent failure, not retrying")
            return RetryDecision.abort(
                f"Permanent failure: {classification.value} - {str(failure)}"
            )

        # Check if max attempts exceeded
        if attempt >= self._max_attempts:
            logger.debug(f"Event {event.event_id}: max attempts ({self._max_attempts}) exceeded")
            return RetryDecision.abort(f"Max attempts ({self._max_attempts}) exceeded")

        # Retry with configured delay
        logger.debug(f"Event {event.event_id}: retrying (attempt {attempt + 1}/{self._max_attempts})")
        return RetryDecision.retry(
            delay_ms=self._delay_ms,
            reason=f"Retry attempt {attempt + 1} of {self._max_attempts}",
        )

    def classify_failure(self, failure: Exception) -> FailureClassification:
        """
        Classify the type of failure.

        Args:
            failure: The exception to classify

        Returns:
            FailureClassification: The classification
        """
        # Check if it's a known recoverable exception
        for exc_type in self._recoverable_exceptions:
            if isinstance(failure, exc_type):
                return FailureClassification.RECOVERABLE

        # Infrastructure errors (database, network, etc.)
        if any(keyword in str(failure).lower() for keyword in ["connection", "timeout", "unavailable"]):
            return FailureClassification.INFRASTRUCTURE

        # Configuration errors
        if any(keyword in str(failure).lower() for keyword in ["config", "setting"]):
            return FailureClassification.CONFIGURATION

        # Programming errors (bugs)
        if isinstance(failure, (TypeError, ValueError, AttributeError, KeyError)):
            return FailureClassification.PROGRAMMING

        # Default: assume recoverable
        return FailureClassification.RECOVERABLE

    def get_max_attempts(self) -> int:
        """
        Get the maximum number of retry attempts.

        Returns:
            The maximum number of attempts
        """
        return self._max_attempts

    @property
    def delay_ms(self) -> int:
        """Get the current delay between retries."""
        return self._delay_ms