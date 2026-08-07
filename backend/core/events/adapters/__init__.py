"""
Event Adapters
==============

This package contains adapters that wrap existing implementations
to conform to canonical interfaces.

ADR Reference: ADR-034
"""

from backend.core.events.adapters.infrastructure import InfrastructureEventBusAdapter
from backend.core.events.adapters.dispatcher import DispatcherAdapter

try:
    from backend.core.events.adapters.router import RouterAdapter
except ImportError:
    RouterAdapter = None

__all__ = [
    "InfrastructureEventBusAdapter",
    "DispatcherAdapter",
    "RouterAdapter",
]