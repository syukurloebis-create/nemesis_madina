"""
Event Bus
Central event routing and orchestration
"""
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
import asyncio
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventPriority(str, Enum):
    """Event priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class EventStatus(str, Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class Event:
    """Event structure"""
    id: UUID = field(default_factory=uuid4)
    type: str = ""
    source: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    status: EventStatus = EventStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "type": self.type,
            "source": self.source,
            "payload": self.payload,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "error": self.error,
            "metadata": self.metadata
        }


@dataclass
class EventSubscription:
    """Event subscription"""
    event_type: str
    handler: Callable[[Event], Awaitable[None]]
    priority: EventPriority = EventPriority.NORMAL
    active: bool = True


class EventBus:
    """
    Event Bus
    Central event routing and orchestration
    """

    def __init__(self):
        self.subscriptions: Dict[str, List[EventSubscription]] = defaultdict(list)
        self.event_history: List[Event] = []
        self.max_history = 1000
        self._processing = False
        self._queue: List[Event] = []
        self._retry_queue: List[Event] = []

    def subscribe(
        self,
        event_type: str,
        handler: Callable[[Event], Awaitable[None]],
        priority: EventPriority = EventPriority.NORMAL
    ) -> None:
        """Subscribe to an event type"""
        subscription = EventSubscription(
            event_type=event_type,
            handler=handler,
            priority=priority
        )
        self.subscriptions[event_type].append(subscription)
        logger.info(f"Subscription added for event: {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe from an event type"""
        if event_type in self.subscriptions:
            self.subscriptions[event_type] = [
                s for s in self.subscriptions[event_type]
                if s.handler != handler
            ]
            logger.info(f"Subscription removed for event: {event_type}")

    def publish(self, event: Event) -> None:
        """Publish an event"""
        self._queue.append(event)
        self.event_history.append(event)

        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]

        logger.debug(f"Event published: {event.type} ({event.id})")

    async def process(self) -> None:
        """Process all pending events"""
        if self._processing:
            return

        self._processing = True

        try:
            # Process regular queue
            while self._queue:
                event = self._queue.pop(0)
                await self._process_event(event)

            # Process retry queue
            while self._retry_queue:
                event = self._retry_queue.pop(0)
                await self._process_event(event)

        finally:
            self._processing = False

    async def _process_event(self, event: Event) -> None:
        """Process a single event"""
        event.status = EventStatus.PROCESSING
        event.processed_at = datetime.now()

        try:
            # Get subscribers for this event type
            subscribers = self.subscriptions.get(event.type, [])

            if not subscribers:
                event.status = EventStatus.COMPLETED
                logger.warning(f"No subscribers for event: {event.type}")
                return

            # Sort by priority
            priority_order = {
                EventPriority.CRITICAL: 0,
                EventPriority.HIGH: 1,
                EventPriority.NORMAL: 2,
                EventPriority.LOW: 3
            }
            subscribers.sort(key=lambda x: priority_order.get(x.priority, 2))

            # Execute handlers
            for subscription in subscribers:
                if subscription.active:
                    await subscription.handler(event)

            event.status = EventStatus.COMPLETED
            logger.debug(f"Event processed: {event.type} ({event.id})")

        except Exception as e:
            event.error = str(e)
            event.retry_count += 1

            if event.retry_count < event.max_retries:
                event.status = EventStatus.RETRY
                self._retry_queue.append(event)
                logger.warning(f"Event retry scheduled: {event.type} ({event.id}), attempt {event.retry_count}")
            else:
                event.status = EventStatus.FAILED
                logger.error(f"Event failed: {event.type} ({event.id}): {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        total = len(self.event_history)
        by_status = {}
        by_type = {}
        pending = len(self._queue)

        for event in self.event_history:
            by_status[event.status.value] = by_status.get(event.status.value, 0) + 1
            by_type[event.type] = by_type.get(event.type, 0) + 1

        return {
            "total_events": total,
            "pending_events": pending,
            "by_status": by_status,
            "by_type": by_type,
            "subscriptions": {k: len(v) for k, v in self.subscriptions.items()}
        }


# Singleton instance
event_bus = EventBus()
