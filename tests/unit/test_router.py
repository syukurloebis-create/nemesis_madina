"""
Unit Tests for Router Components
================================

Tests the DefaultRouter and RoutingRegistry implementations.
"""

import pytest

from backend.core.events.interfaces.router import Job, RoutingDecision, RoutingDestination
from backend.core.events.routing import DefaultRouter, RoutingRegistry
from backend.core.events.routing.registry import RoutingRule


class TestRoutingRegistry:
    """Tests for RoutingRegistry."""

    def test_register_exact_match(self):
        """Test registering an exact match route."""
        registry = RoutingRegistry()
        registry.register("order.created", RoutingDestination.WORKER)

        destination = registry.get_destination("order.created")
        assert destination == RoutingDestination.WORKER

    def test_register_wildcard_match(self):
        """Test registering a wildcard route."""
        registry = RoutingRegistry()
        registry.register("order.*", RoutingDestination.WORKER)

        destination = registry.get_destination("order.created")
        assert destination == RoutingDestination.WORKER

    def test_register_wildcard_with_priority(self):
        """Test wildcard matching with priority."""
        registry = RoutingRegistry()
        registry.register("order.*", RoutingDestination.WORKER, priority=0)
        registry.register("order.created", RoutingDestination.IMMEDIATE, priority=1)

        destination = registry.get_destination("order.created")
        assert destination == RoutingDestination.IMMEDIATE

    def test_unregister(self):
        """Test unregistering a route."""
        registry = RoutingRegistry()
        registry.register("order.created", RoutingDestination.WORKER)

        assert registry.unregister("order.created") is True
        assert registry.get_destination("order.created") == RoutingDestination.IMMEDIATE

    def test_default_destination(self):
        """Test default destination for unknown event types."""
        registry = RoutingRegistry()
        registry.set_default_destination(RoutingDestination.ANALYTICS)

        destination = registry.get_destination("unknown.event")
        assert destination == RoutingDestination.ANALYTICS

    def test_clear(self):
        """Test clearing all rules."""
        registry = RoutingRegistry()
        registry.register("order.created", RoutingDestination.WORKER)
        registry.register("payment.*", RoutingDestination.ANALYTICS)

        registry.clear()
        assert len(registry.get_all_rules()) == 0


class TestDefaultRouter:
    """Tests for DefaultRouter."""

    def test_route_exact_match(self):
        """Test routing with exact match."""
        router = DefaultRouter()
        router.register_route("order.created", RoutingDestination.WORKER)

        job = Job("order.created", {})
        decision = router.route(job)

        assert decision.destination == RoutingDestination.WORKER

    def test_route_wildcard_match(self):
        """Test routing with wildcard match."""
        router = DefaultRouter()
        router.register_route("order.*", RoutingDestination.WORKER)

        job = Job("order.created", {})
        decision = router.route(job)

        assert decision.destination == RoutingDestination.WORKER

    def test_route_unknown_event(self):
        """Test routing unknown event returns default."""
        router = DefaultRouter()
        router.set_default_destination(RoutingDestination.ANALYTICS)

        job = Job("unknown.event", {})
        decision = router.route(job)

        assert decision.destination == RoutingDestination.ANALYTICS

    def test_route_with_priority(self):
        """Test routing with priority ordering."""
        router = DefaultRouter()
        router.register_route("order.*", RoutingDestination.WORKER, priority=0)
        router.register_route("order.created", RoutingDestination.IMMEDIATE, priority=1)

        job = Job("order.created", {})
        decision = router.route(job)

        assert decision.destination == RoutingDestination.IMMEDIATE

    def test_route_raises_on_invalid_job(self):
        """Test that route raises ValueError for invalid job."""
        router = DefaultRouter()

        with pytest.raises(ValueError, match="Job cannot be None"):
            router.route(None)

        with pytest.raises(ValueError, match="event_type cannot be empty"):
            router.route(Job("", {}))

    def test_get_default_destination(self):
        """Test getting default destination."""
        router = DefaultRouter()
        assert router.get_default_destination() == RoutingDestination.IMMEDIATE

        router.set_default_destination(RoutingDestination.ANALYTICS)
        assert router.get_default_destination() == RoutingDestination.ANALYTICS

    def test_register_and_unregister(self):
        """Test registering and unregistering routes."""
        router = DefaultRouter()
        router.register_route("order.created", RoutingDestination.WORKER)

        job = Job("order.created", {})
        decision = router.route(job)
        assert decision.destination == RoutingDestination.WORKER

        router.unregister_route("order.created")
        decision = router.route(job)
        assert decision.destination == RoutingDestination.IMMEDIATE