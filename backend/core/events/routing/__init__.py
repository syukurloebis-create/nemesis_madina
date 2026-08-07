"""
Routing Package
===============

Event routing components for the canonical event architecture.

ADR Reference: ADR-033
"""

from backend.core.events.routing.default_router import DefaultRouter
from backend.core.events.routing.registry import RoutingRegistry

# Import from interfaces so we can re-export
from backend.core.events.interfaces.router import RoutingDestination

__all__ = [
    "DefaultRouter",
    "RoutingRegistry",
    "RoutingDestination",
]