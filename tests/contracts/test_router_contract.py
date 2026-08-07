"""
Contract Tests for IEventRouter
===============================

Verifies that router implementations satisfy the IEventRouter contract.

ADR Reference: ADR-033
"""

import pytest

from backend.core.events.interfaces.router import IEventRouter, Job, RoutingDestination
from backend.core.events.routing import DefaultRouter
from backend.core.events.adapters import RouterAdapter
from backend.core.events.interfaces.router import RoutingDecision


class TestIEventRouterContract:
    """Contract tests for IEventRouter implementations."""

    @pytest.fixture
    def routers(self):
        """Get all router implementations to test."""
        return [
            DefaultRouter(),
            # RouterAdapter(),  
        ]

    def test_route_returns_routing_decision(self, routers):
        """Test that route returns a RoutingDecision."""
        for router in routers:
            if router is None:
                continue

            job = Job("test.event", {})
            decision = router.route(job)

            assert isinstance(decision, RoutingDecision)
            assert decision.destination in RoutingDestination

    def test_route_raises_on_empty_event_type(self, routers):
        """Test that route raises ValueError for empty event_type."""
        for router in routers:
            if router is None:
                continue

            with pytest.raises(ValueError, match="event_type cannot be empty"):
                router.route(Job("", {}))

    def test_route_raises_on_none_job(self, routers):
        """Test that route raises ValueError for None job."""
        for router in routers:
            if router is None:
                continue

            with pytest.raises(ValueError, match="Job cannot be None"):
                router.route(None)

    def test_get_default_destination_returns_destination(self, routers):
        """Test that get_default_destination returns a RoutingDestination."""
        for router in routers:
            if router is None:
                continue

            destination = router.get_default_destination()
            assert destination in RoutingDestination

    def test_router_implements_interface(self, routers):
        """Test that router implementations implement IEventRouter."""
        for router in routers:
            if router is None:
                continue

            assert isinstance(router, IEventRouter)