# backend/dashboard/protocols/circuit_breaker.py

from typing import Protocol, Optional
from enum import StrEnum


class CircuitBreaker(Protocol):
    """Protocol for circuit breakers."""

    def is_available(self) -> bool:
        """Check if circuit is available (not open)."""
        ...

    def record_failure(self) -> None:
        """Record a failure."""
        ...

    def record_success(self) -> None:
        """Record a success."""
        ...

    def get_state(self) -> str:
        """Get current circuit state: 'closed', 'open', 'half_open'."""
        ...

class CircuitState(StrEnum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker(Protocol):
    def get_state(self) -> CircuitState:
        ...

class MemoryCircuitBreaker:
    """Simple in-memory circuit breaker for testing/development."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout_seconds: float = 30.0
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self._failure_count = 0
        self._state = "closed"  # closed, open, half_open
        self._last_failure_time = None

    def record_failure(self) -> None:
        import time
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self.failure_threshold:
            self._state = "open"

    def record_success(self) -> None:
        if self._state == "half_open":
            self._state = "closed"
            self._failure_count = 0
        else:
            # Reset failure count on success
            self._failure_count = max(0, self._failure_count - 1)

    def get_state(self) -> str:
        return self._state

    def reset(self) -> None:
        """Reset circuit breaker."""
        self._failure_count = 0
        self._state = "closed"
        self._last_failure_time = None


class NoOpCircuitBreaker:
    """No-op circuit breaker (always available)."""

    def is_available(self) -> bool:
        return True

    def record_failure(self) -> None:
        pass

    def record_success(self) -> None:
        pass

    def get_state(self) -> str:
        return "closed"