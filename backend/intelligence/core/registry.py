"""
In-memory event registry for IntelligenceEngine.

Legacy compatibility layer. Only used by tests.
Remove after Sprint 4.x if IntelligenceEngine is deprecated.
"""

from typing import List, Any


class EventRegistry:
    """
    Lightweight in-memory registry used by the legacy
    IntelligenceEngine audit pipeline.

    This class is intentionally independent from:
    - backend.domain.event_registry (schema registry)
    - backend.orchestrator.registry (job registry)
    """

    def __init__(self):
        self._events: List[Any] = []

    def register(self, event: Any) -> None:
        """Register an event."""
        self._events.append(event)

    def get_all(self) -> List[Any]:
        """Get all registered events."""
        return list(self._events)

    def clear(self) -> None:
        """Clear all events."""
        self._events.clear()