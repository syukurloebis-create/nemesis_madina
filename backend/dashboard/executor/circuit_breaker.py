# backend/dashboard/executor/circuit_breaker.py

from typing import Dict, Optional
from enum import StrEnum


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class MemoryCircuitBreaker:
    """In-memory circuit breaker - self-managed state."""
    # ... (implementation unchanged)


class CircuitBreakerRegistry:
    """
    Registry for circuit breakers - NO GLOBAL STATE.
    
    Created at bootstrap and passed to components.
    Easy to test, no singleton pollution.
    """
    
    def __init__(self):
        self._breakers: Dict[str, MemoryCircuitBreaker] = {}
    
    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout_seconds: float = 30.0
    ) -> MemoryCircuitBreaker:
        if name not in self._breakers:
            self._breakers[name] = MemoryCircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                timeout_seconds=timeout_seconds
            )
        return self._breakers[name]
    
    def reset_all(self) -> None:
        for breaker in self._breakers.values():
            breaker.reset()
    
    def get_state(self, name: str) -> Optional[CircuitState]:
        breaker = self._breakers.get(name)
        return breaker.get_state() if breaker else None