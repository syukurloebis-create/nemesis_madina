"""
Graph Infrastructure - Clock Interface
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone


class Clock(ABC):
    """Abstract clock for time operations."""
    
    @abstractmethod
    def now(self) -> datetime:
        """Get current UTC datetime."""
        pass


class SystemClock(Clock):
    """System clock implementation."""
    
    def now(self) -> datetime:
        return datetime.now(timezone.utc)