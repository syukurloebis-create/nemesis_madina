"""
Event Retry Policy Interface
============================

Defines the IEventRetryPolicy interface for retry decisions.

ADR Reference: ADR-033
Requirements: REQ-RET-001
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from backend.core.events.interfaces.event import IEvent


@dataclass(frozen=True)
class RetryDecision:
    """
    The result of a retry evaluation.

    Contains whether to retry and the delay before next attempt.
    Immutable by design.
    """
    should_retry: bool
    delay_ms: int = 0
    reason: Optional[str] = None

    @classmethod
    def retry(cls, delay_ms: int = 100, reason: str = "Retry requested") -> "RetryDecision":
        """Create a retry decision."""
        return cls(True, delay_ms, reason)

    @classmethod
    def abort(cls, reason: str = "Abort requested") -> "RetryDecision":
        """Create an abort decision."""
        return cls(False, 0, reason)

    def __repr__(self) -> str:
        return f"<RetryDecision(retry={self.should_retry}, delay={self.delay_ms}ms)>"


class FailureClassification(str, Enum):
    """Classification of failure types."""
    RECOVERABLE = "recoverable"
    PERMANENT = "permanent"
    CONFIGURATION = "configuration"
    PROGRAMMING = "programming"
    INFRASTRUCTURE = "infrastructure"


class IEventRetryPolicy(ABC):
    """
    Event Retry Policy Contract.

    Determines if a failed event should be retried.

    Semantics (ADR-032):
    - Retry: Re-attempt a failed dispatch
    - Maximum attempts: Configurable
    - Exponential backoff: Optional
    """

    @abstractmethod
    def evaluate(
        self,
        event: IEvent,
        attempt: int,
        failure: Exception,
    ) -> RetryDecision:
        """
        Evaluate whether to retry a failed event.

        Precondition: event is not None
        Precondition: attempt is >= 0
        Postcondition: retry decision is returned
        Postcondition: decision is deterministic

        Args:
            event: The event that failed
            attempt: The current attempt number (0-based)
            failure: The exception that occurred

        Returns:
            RetryDecision: Whether to retry and with what delay
        """
        pass

    @abstractmethod
    def classify_failure(self, failure: Exception) -> FailureClassification:
        """
        Classify the type of failure.

        Args:
            failure: The exception to classify

        Returns:
            FailureClassification: The classification
        """
        pass

    @abstractmethod
    def get_max_attempts(self) -> int:
        """
        Get the maximum number of retry attempts.

        Returns:
            The maximum number of attempts
        """
        pass