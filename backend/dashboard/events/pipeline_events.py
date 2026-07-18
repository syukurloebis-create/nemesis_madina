# backend/dashboard/events/pipeline_events.py

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any, List, Protocol

# ✅ Add logger
logger = logging.getLogger(__name__)


# ============================================================================
# METRICS RECORDER PROTOCOL
# ============================================================================

class MetricsRecorder(Protocol):
    """Protocol for metrics recorder."""
    
    def record_pipeline(self, name: str, duration_ms: float, success: bool) -> None:
        """Record pipeline execution."""
        ...
    
    def record_pipeline_timeout(self, name: str) -> None:
        """Record pipeline timeout."""
        ...


# ============================================================================
# EVENTS (with kw_only=True)
# ============================================================================

@dataclass(slots=True, frozen=True, kw_only=True)
class PipelineEvent:
    """Base pipeline event."""
    name: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(slots=True, frozen=True, kw_only=True)
class PipelineStartedEvent(PipelineEvent):
    """Pipeline execution started."""
    pass


@dataclass(slots=True, frozen=True, kw_only=True)
class PipelineFinishedEvent(PipelineEvent):
    """Pipeline execution finished."""
    duration_ms: float
    success: bool
    result: Optional[Any] = None


@dataclass(slots=True, frozen=True, kw_only=True)
class PipelineFailedEvent(PipelineEvent):
    """Pipeline execution failed."""
    error: Exception


@dataclass(slots=True, frozen=True, kw_only=True)
class PipelineTimeoutEvent(PipelineEvent):
    """Pipeline execution timed out."""
    timeout_seconds: float


# ============================================================================
# EVENT BUS
# ============================================================================

class EventSubscriber(Protocol):
    """Protocol for event subscribers."""

    async def handle(self, event: PipelineEvent) -> None:
        """Handle pipeline event."""
        ...


class EventBus:
    """Simple event bus for pipeline events."""

    def __init__(self):
        self._subscribers: List[EventSubscriber] = []

    def subscribe(self, subscriber: EventSubscriber) -> None:
        """Register a subscriber."""
        self._subscribers.append(subscriber)

    async def publish(self, event: PipelineEvent) -> None:
        """Publish event to all subscribers."""
        for subscriber in self._subscribers:
            try:
                await subscriber.handle(event)
            except Exception as e:
                logger.error(f"Event subscriber error: {e}")


# ============================================================================
# SUBSCRIBERS
# ============================================================================

class MetricsSubscriber:
    """Subscribes to pipeline events and records metrics."""

    def __init__(self, metrics: MetricsRecorder):
        self._metrics = metrics

    async def handle(self, event: PipelineEvent) -> None:
        if isinstance(event, PipelineFinishedEvent):
            self._metrics.record_pipeline(
                name=event.name,
                duration_ms=event.duration_ms,
                success=event.success
            )
        elif isinstance(event, PipelineFailedEvent):
            self._metrics.record_pipeline(
                name=event.name,
                duration_ms=0.0,
                success=False
            )
        elif isinstance(event, PipelineTimeoutEvent):
            self._metrics.record_pipeline_timeout(event.name)


class AuditSubscriber:
    """Records audit trail for pipeline executions."""

    def __init__(self, audit_logger):
        self._audit_logger = audit_logger

    async def handle(self, event: PipelineEvent) -> None:
        # Audit logic here
        pass