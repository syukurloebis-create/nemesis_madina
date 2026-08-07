"""
Router Adapter
==============

Wraps existing EventBusV2 to conform to IEventRouter.

ADR Reference: ADR-034
"""

import logging
import importlib
from typing import Optional, TYPE_CHECKING

from backend.core.events.interfaces.router import IEventRouter, Job, RoutingDecision, RoutingDestination

logger = logging.getLogger(__name__)


class RouterAdapter(IEventRouter):
    """
    Adapter for EventBusV2.

    Uses LAZY IMPORT to avoid hard dependency on orchestrator.
    The underlying EventBusV2 is only imported when actually used.

    Does NOT change semantics — only API transformation.
    """

    def __init__(self, router: Optional[object] = None):
        """
        Initialize the router adapter.

        Args:
            router: The existing EventBusV2 instance.
                    If None, lazy-loads EventBusV2 when first used.
        """
        self._router = router
        self._lazy_loaded = False
        logger.info("RouterAdapter initialized (lazy-load mode)")

    def _ensure_router(self) -> None:
        """
        Lazy-load EventBusV2 if not already loaded.
        """
        if self._lazy_loaded:
            return

        if self._router is not None:
            self._lazy_loaded = True
            return

        try:
            # Lazy import: only import when actually needed
            module = importlib.import_module("backend.orchestrator.event_bus_v2")
            EventBusV2 = getattr(module, "EventBusV2")
            self._router = EventBusV2()
            self._lazy_loaded = True
            logger.info("RouterAdapter: EventBusV2 lazy-loaded successfully")
        except (ImportError, AttributeError) as e:
            logger.warning(f"RouterAdapter: EventBusV2 not available: {e}")
            raise ImportError(
                "EventBusV2 not available. Please ensure backend.orchestrator.event_bus_v2 exists."
            ) from e

    def route(self, job: Job) -> RoutingDecision:
        """
        Route a job using the underlying EventBusV2.

        Lazy-loads EventBusV2 on first call.
        """
        self._ensure_router()

        if job is None:
            raise ValueError("Job cannot be None")

        if not job.event_type:
            raise ValueError("event_type cannot be empty")

        logger.debug(f"Routing {job.event_type} via EventBusV2")

        # Delegate to underlying router
        if hasattr(self._router, "route"):
            result = self._router.route(job)
            if isinstance(result, RoutingDecision):
                return result
            else:
                return RoutingDecision(RoutingDestination.WORKER)
        else:
            logger.warning("EventBusV2.route() not found. Using default destination.")
            return RoutingDecision(self.get_default_destination())

    def get_default_destination(self) -> RoutingDestination:
        """
        Get the default destination for unknown event types.
        """
        self._ensure_router()

        if hasattr(self._router, "get_default_destination"):
            return self._router.get_default_destination()
        return RoutingDestination.WORKER

    @property
    def underlying_router(self):
        """Get the underlying EventBusV2 instance."""
        self._ensure_router()
        return self._router