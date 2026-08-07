"""
Canonical Event Interfaces
==========================

This package defines the canonical interfaces for the EventBus system
as specified in ADR-033.

All implementations MUST adhere to these interfaces.
"""

from backend.core.events.interfaces.event import IEvent, BaseEvent
from backend.core.events.interfaces.publisher import IEventPublisher
from backend.core.events.interfaces.subscriber import IEventSubscriber
from backend.core.events.interfaces.router import IEventRouter, Job, RoutingDecision, RoutingDestination
from backend.core.events.interfaces.retry import IEventRetryPolicy, RetryDecision, FailureClassification
from backend.core.events.interfaces.dead_letter import IDeadLetterStore, DeadLetterEntry

__all__ = [
    # Event Contract
    "IEvent",
    "BaseEvent",
    # Publisher
    "IEventPublisher",
    # Subscriber
    "IEventSubscriber",
    # Router
    "IEventRouter",
    "Job",
    "RoutingDecision",
    "RoutingDestination",
    # Retry
    "IEventRetryPolicy",
    "RetryDecision",
    "FailureClassification",
    # Dead Letter
    "IDeadLetterStore",
    "DeadLetterEntry",
]