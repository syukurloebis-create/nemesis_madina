"""
Exponential Backoff Retry Policy
================================

Exponential backoff implementation with optional jitter.

ADR Reference: ADR-033
"""

import logging
import random
import time
from typing import Optional

from backend.core.events.retry.default_retry import DefaultRetryPolicy
from backend.core.events.interfaces.retry import RetryDecision
from backend.core.events.interfaces.event import IEvent

logger = logging.getLogger(__name__)


class ExponentialBackoffRetryPolicy(DefaultRetryPolicy):
    """
    Exponential backoff retry policy.

    Features:
    - Exponential backoff: delay = base_delay * (multiplier ^ attempt)
    - Optional jitter to prevent thundering herd
    - Configurable max delay
    - Inherits classification from DefaultRetryPolicy
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay_ms: int = 100,
        multiplier: float = 2.0,
        max_delay_ms: Optional[int] = None,
        jitter: bool = False,
        recoverable_exceptions: Optional[list[type[Exception]]] = None,
    ):
        """
        Initialize the exponential backoff retry policy.

        Args:
            max_attempts: Maximum number of retry attempts
            base_delay_ms: Initial delay in milliseconds
            multiplier: Multiplier for each subsequent attempt
            max_delay_ms: Maximum delay cap in milliseconds
            jitter: Whether to add random jitter
            recoverable_exceptions: List of exception types considered recoverable
        """
        super().__init__(
            max_attempts=max_attempts,
            delay_ms=base_delay_ms,
            recoverable_exceptions=recoverable_exceptions,
        )
        self._base_delay_ms = base_delay_ms
        self._multiplier = multiplier
        self._max_delay_ms = max_delay_ms or (base_delay_ms * (multiplier ** max_attempts))
        self._jitter = jitter

        logger.info(
            f"ExponentialBackoffRetryPolicy initialized "
            f"(base={base_delay_ms}ms, multiplier={multiplier}, "
            f"max_delay={self._max_delay_ms}ms, jitter={jitter})"
        )

    def evaluate(
        self,
        event: IEvent,
        attempt: int,
        failure: Exception,
    ) -> RetryDecision:
        """
        Evaluate whether to retry with exponential backoff.

        Args:
            event: The event that failed
            attempt: The current attempt number (0-based)
            failure: The exception that occurred

        Returns:
            RetryDecision: Whether to retry and with what delay
        """
        # First, check if we should retry at all
        base_decision = super().evaluate(event, attempt, failure)

        if not base_decision.should_retry:
            return base_decision

        # Calculate exponential backoff delay
        delay_ms = self._base_delay_ms * (self._multiplier ** attempt)

        # Cap at max delay
        if delay_ms > self._max_delay_ms:
            delay_ms = self._max_delay_ms

        # Add jitter if enabled
        if self._jitter:
            jitter_factor = random.uniform(0.5, 1.5)
            delay_ms = delay_ms * jitter_factor

        return RetryDecision.retry(
            delay_ms=int(delay_ms),
            reason=f"Exponential backoff (attempt {attempt + 1}/{self._max_attempts})",
        )