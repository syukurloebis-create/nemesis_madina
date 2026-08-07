"""
Canonical Event System — PUBLIC API
===================================

This package exports the PUBLIC API for the event system.
Infrastructure implementations are available via submodules.
"""

from backend.core.events.interfaces import (
    IEvent,
    BaseEvent,
    IEventPublisher,
    IEventSubscriber,
    IEventRouter,
    IEventRetryPolicy,
    IDeadLetterStore,
    Job,
    RoutingDecision,
    RoutingDestination,
    RetryDecision,
    FailureClassification,
    DeadLetterEntry,
)
from backend.core.events.interfaces.subscriber import EventHandler
from backend.core.events.facade import EventBusFacade
from backend.core.events.routing import DefaultRouter, RoutingRegistry
from backend.core.events.retry import DefaultRetryPolicy, ExponentialBackoffRetryPolicy
from backend.core.events.dead_letter import InMemoryDeadLetterStore, FileBasedDeadLetterStore
from backend.core.events.null_objects import (
    NullEventRouter,
    NullEventRetryPolicy,
    NullDeadLetterStore,
)
from backend.core.events.legacy_compat import LegacyEventBusWrapper
from backend.core.events.events import EventFactory, DomainEvent, create_event

Event = DomainEvent
EventBus = LegacyEventBusWrapper

try:
    from backend.core.events.normalizer import EventNormalizer
    normalizer = EventNormalizer()
except ImportError:
    class EventNormalizer:
        @staticmethod
        def normalize(event):
            return event
    normalizer = EventNormalizer

try:
    from backend.infrastructure.event_bus import InMemoryEventBus as _InMemoryEventBus
    InMemoryEventBus = _InMemoryEventBus
except ImportError:
    InMemoryEventBus = None

# ===== ADAPTERS (NOT exported from root — import from adapters directly) =====
# InfrastructureEventBusAdapter, DispatcherAdapter, RouterAdapter are available at:
#   from backend.core.events.adapters import InfrastructureEventBusAdapter

__all__ = [
    # Contracts
    "IEvent",
    "BaseEvent",
    "IEventPublisher",
    "IEventSubscriber",
    "IEventRouter",
    "IEventRetryPolicy",
    "IDeadLetterStore",
    "EventHandler",
    "Job",
    "RoutingDecision",
    "RoutingDestination",
    "RetryDecision",
    "FailureClassification",
    "DeadLetterEntry",
    # Facade
    "EventBusFacade",
    # Events
    "DomainEvent",
    "EventFactory",
    "create_event",
    # Routing
    "DefaultRouter",
    "RoutingRegistry",
    # Retry
    "DefaultRetryPolicy",
    "ExponentialBackoffRetryPolicy",
    # Dead Letter
    "InMemoryDeadLetterStore",
    "FileBasedDeadLetterStore",
    # Null Objects
    "NullEventRouter",
    "NullEventRetryPolicy",
    "NullDeadLetterStore",
    # Legacy
    "EventBus",
    "InMemoryEventBus",
    "normalizer",
]