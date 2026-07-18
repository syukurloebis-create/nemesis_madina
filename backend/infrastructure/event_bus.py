"""
Event Bus — Interface + Implementations.

Architecture Decision:
- IEventBus is the contract (Interface)
- Multiple implementations: InMemory, Kafka, RabbitMQ
- Collectors publish events, subscribers handle them
- Async event processing
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Awaitable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class DomainEvent:

    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass(frozen=True)
class DashboardGeneratedEvent(DomainEvent):
    """
    Published when dashboard is generated.
    
    IMPORTANT: Fields with defaults (from DomainEvent) come FIRST,
    then fields without defaults come AFTER.
    """
    # Fields without defaults FIRST (mengikuti aturan dataclass)
    case_id: UUID
    status: str
    confidence: float
    duration_ms: float
    
    # Override event_type with default
    event_type: str = field(default_factory=lambda: "DashboardGeneratedEvent")


@dataclass(frozen=True)
class CollectorCompletedEvent(DomainEvent):
    """Published when a collector completes."""
    # Fields without defaults FIRST
    collector: str
    case_id: UUID
    duration_ms: float
    rows_returned: int
    
    event_type: str = field(default_factory=lambda: "CollectorCompletedEvent")


@dataclass(frozen=True)
class CollectorFailedEvent(DomainEvent):
    """Published when a collector fails."""
    # Fields without defaults FIRST
    collector: str
    case_id: UUID
    error: str
    fallback_reason: str
    
    event_type: str = field(default_factory=lambda: "CollectorFailedEvent")


class IEventBus(ABC):
    """Event Bus Interface — Contract for all implementations."""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers."""
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], Awaitable[None]]) -> "IEventBus":
        """Subscribe to an event type."""
        pass


class InMemoryEventBus(IEventBus):
    """
    In-Memory Event Bus — Default Implementation.
    
    Characteristics:
    - Async event processing
    - Subscriber registry
    - Error handling (subscriber errors don't break publishing)
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[DomainEvent], Awaitable[None]]]] = {}
        self._lock = asyncio.Lock()
    
    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], Awaitable[None]]) -> "IEventBus":
        """Subscribe to an event type."""
        async def _add_subscriber():
            async with self._lock:
                if event_type not in self._subscribers:
                    self._subscribers[event_type] = []
                self._subscribers[event_type].append(handler)
                logger.debug(f"Subscribed to {event_type} (total: {len(self._subscribers[event_type])})")
        
        asyncio.create_task(_add_subscriber())
        return self
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers."""
        event_type = event.event_type
        subscribers = self._subscribers.get(event_type, [])
        
        if not subscribers:
            logger.debug(f"No subscribers for {event_type}")
            return
        
        logger.debug(f"Publishing {event_type} to {len(subscribers)} subscribers")
        
        # Execute all subscribers in parallel
        tasks = []
        for handler in subscribers:
            tasks.append(self._safe_handler(handler, event))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_handler(self, handler: Callable, event: DomainEvent) -> None:
        """Execute handler with error handling."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Event handler failed for {event.event_type}: {e}", exc_info=True)