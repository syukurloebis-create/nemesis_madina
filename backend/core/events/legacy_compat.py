"""
Legacy Compatibility Wrapper
============================

Provides backward compatibility for existing consumers.

ADR Reference: ADR-036

DESIGN: This wrapper is injected with the facade.
It does NOT import bootstrap to avoid circular imports.
"""

import logging
from typing import Optional, Any, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class LegacyEventBusWrapper:
    """
    Wraps the new EventBusFacade to mimic the old EventBus API.

    This allows existing code to continue working during migration.

    DESIGN: Dependencies are injected via constructor.
    No circular imports.
    """

    _instance: Optional['LegacyEventBusWrapper'] = None

    def __init__(self, facade: Any):
        """
        Initialize the wrapper with a facade instance.

        Args:
            facade: The EventBusFacade instance to wrap
        """
        self._facade = facade
        logger.info("LegacyEventBusWrapper initialized with facade")

    @classmethod
    def get_instance(cls, facade: Any = None) -> 'LegacyEventBusWrapper':
        """
        Get the singleton instance.

        Args:
            facade: The facade to use (only used on first creation)

        Returns:
            LegacyEventBusWrapper: The singleton instance
        """
        if cls._instance is None:
            if facade is None:
                raise ValueError(
                    "LegacyEventBusWrapper not initialized. "
                    "Please call get_instance(facade) first."
                )
            cls._instance = cls(facade)
        return cls._instance

    @property
    def facade(self):
        """Get the underlying facade."""
        if self._facade is None:
            raise RuntimeError("LegacyEventBusWrapper not properly initialized")
        return self._facade

    # ===== Old EventBus API =====

    def publish(self, event: Any) -> None:
        """
        Publish an event (synchronous wrapper for backward compatibility).

        This is a synchronous wrapper for the async publish method.
        """
        import asyncio
        from backend.core.events.events import EventFactory
        from backend.core.events.interfaces import BaseEvent

        # Convert event to canonical format if needed
        if not isinstance(event, BaseEvent):
            if isinstance(event, dict):
                event = EventFactory.create(
                    event_type=event.get('type', 'unknown'),
                    payload=event.get('data', {})
                )
            else:
                event = EventFactory.create(
                    event_type=event.__class__.__name__,
                    payload=event.__dict__ if hasattr(event, '__dict__') else {}
                )

        # Run async publish synchronously
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.facade.publish(event))
                loop.close()
            else:
                loop.run_until_complete(self.facade.publish(event))
        except RuntimeError:
            asyncio.run(self.facade.publish(event))

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to events (legacy API)."""
        import asyncio

        if not asyncio.iscoroutinefunction(handler):
            async def async_handler(event):
                return handler(event)
            actual_handler = async_handler
        else:
            actual_handler = handler

        self.facade.subscribe(event_type, actual_handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe from events (legacy API)."""
        self.facade.unsubscribe(event_type, handler)

    def get_handlers(self, event_type: str) -> list:
        """Get handlers for an event type."""
        return self.facade.get_handlers(event_type)

    # ===== Additional compatibility methods =====

    def route(self, job: Any) -> Any:
        """Route a job (legacy API)."""
        return self.facade.route(job)

    def evaluate_retry(self, event: Any, attempt: int, failure: Exception) -> Any:
        """Evaluate retry policy (legacy API)."""
        return self.facade.evaluate_retry(event, attempt, failure)

    def classify_failure(self, failure: Exception) -> Any:
        """Classify failure (legacy API)."""
        return self.facade.classify_failure(failure)

    def get_max_retries(self) -> int:
        """Get max retries (legacy API)."""
        return self.facade.get_max_retries()

    def store_dead_letter(self, entry: Any) -> None:
        """Store dead letter (legacy API)."""
        self.facade.store_dead_letter(entry)

    def get_dead_letters(self) -> list:
        """Get dead letters (legacy API)."""
        return self.facade.get_dead_letters()

    def get_dead_letter(self, event_id: str) -> Any:
        """Get dead letter by ID (legacy API)."""
        return self.facade.get_dead_letter(event_id)

    def replay_dead_letter(self, event_id: str) -> bool:
        """Replay dead letter (legacy API)."""
        return self.facade.replay_dead_letter(event_id)

    def remove_dead_letter(self, event_id: str) -> bool:
        """Remove dead letter (legacy API)."""
        return self.facade.remove_dead_letter(event_id)

    def count_dead_letters(self) -> int:
        """Count dead letters (legacy API)."""
        return self.facade.count_dead_letters()

    # ===== Magic methods for attribute forwarding =====

    def __getattr__(self, name: str):
        """Forward unknown attributes to the facade."""
        if self._facade is not None and hasattr(self._facade, name):
            return getattr(self._facade, name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __repr__(self) -> str:
        return f"<LegacyEventBusWrapper(facade={self._facade})>"