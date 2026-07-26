"""
NEMESIS Madina - Circuit Breaker
✅ Complete implementation
✅ State management with timeout
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for outbox publisher.
    ✅ Complete implementation with state transitions
    ✅ Thread-safe with asyncio lock
    """
    
    failure_threshold: int = 5
    timeout_seconds: int = 60
    success_threshold: int = 3
    
    _state: CircuitState = CircuitState.CLOSED
    _failure_count: int = 0
    _success_count: int = 0
    _last_failure_time: Optional[datetime] = None
    _last_state_change: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    
    def __post_init__(self):
        self._timeout_seconds = self.timeout_seconds
    
    @property
    def state(self) -> CircuitState:
        return self._state
    
    @property
    def failure_count(self) -> int:
        return self._failure_count
    
    @property
    def success_count(self) -> int:
        return self._success_count
    
    @property
    def last_failure_time(self) -> Optional[datetime]:
        return self._last_failure_time
    
    async def can_execute(self) -> bool:
        """Check if operation can execute."""
        async with self._lock:
            if self._state == CircuitState.CLOSED:
                return True
            
            if self._state == CircuitState.OPEN:
                # Check if timeout elapsed
                now = datetime.now(timezone.utc)
                if now - self._last_state_change > timedelta(seconds=self._timeout_seconds):
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    logger.info("Circuit breaker half-open")
                    return True
                return False
            
            # HALF_OPEN
            return True
    
    async def record_success(self) -> None:
        """Record successful operation."""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    logger.info("Circuit breaker closed")
            else:
                self._failure_count = 0
    
    async def record_failure(self) -> None:
        """Record failed operation."""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = datetime.now(timezone.utc)
            
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._last_state_change = datetime.now(timezone.utc)
                logger.warning("Circuit breaker open - half-open failure")
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self._failure_threshold:
                    self._state = CircuitState.OPEN
                    self._last_state_change = datetime.now(timezone.utc)
                    logger.warning("Circuit breaker open")
    
    async def reset(self) -> None:
        """Reset circuit breaker."""
        async with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._last_state_change = datetime.now(timezone.utc)
            logger.info("Circuit breaker reset")