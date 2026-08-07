"""
Default Router
==============

Default implementation of IEventRouter.

ADR Reference: ADR-033
"""

import logging
from typing import Dict, Optional

from backend.core.events.interfaces.router import (
    IEventRouter,
    Job,
    RoutingDecision,
    RoutingDestination,
)
from backend.core.events.routing.registry import RoutingRegistry

logger = logging.getLogger(__name__)


class DefaultRouter(IEventRouter):
    """
    Default implementation of IEventRouter.

    Uses a RoutingRegistry to map event types to destinations.
    Supports wildcard matching and priority ordering.
    """

    def __init__(
        self,
        registry: Optional[RoutingRegistry] = None,
        default_destination: Optional[RoutingDestination] = None,
    ):
        """
        Initialize the default router.

        Args:
            registry: Optional routing registry (creates new if None)
            default_destination: Optional default destination
        """
        self._registry = registry or RoutingRegistry()

        if default_destination is not None:
            self._registry.set_default_destination(default_destination)

        logger.info("DefaultRouter initialized")

    def route(self, job: Job) -> RoutingDecision:
        """
        Route a job to an execution destination.

        Args:
            job: The job to route

        Returns:
            RoutingDecision: The routing decision

        Raises:
            ValueError: If job is None or event_type is empty
        """
        if job is None:
            raise ValueError("Job cannot be None")

        if not job.event_type:
            raise ValueError("event_type cannot be empty")

        destination = self._registry.get_destination(job.event_type)

        logger.debug(f"Routing {job.event_type} → {destination.value}")

        return RoutingDecision(
            destination=destination,
            metadata={
                "event_type": job.event_type,
                "routed_at": "now",  # Will be replaced with actual timestamp
            },
        )

    def get_default_destination(self) -> RoutingDestination:
        """Get the default destination for unknown event types."""
        return self._registry.get_default_destination()

    def register_route(
        self,
        event_type: str,
        destination: RoutingDestination,
        priority: int = 0,
    ) -> None:
        """
        Register a routing rule.

        Args:
            event_type: The event type to route
            destination: The destination to route to
            priority: Priority (higher = more specific)
        """
        self._registry.register(event_type, destination, priority)

    def unregister_route(self, event_type: str) -> bool:
        """
        Unregister a routing rule.

        Args:
            event_type: The event type to unregister

        Returns:
            True if removed, False if not found
        """
        return self._registry.unregister(event_type)

    def set_default_destination(self, destination: RoutingDestination) -> None:
        """
        Set the default destination.

        Args:
            destination: The default destination
        """
        self._registry.set_default_destination(destination)

    @property
    def registry(self) -> RoutingRegistry:
        """Get the routing registry."""
        return self._registry