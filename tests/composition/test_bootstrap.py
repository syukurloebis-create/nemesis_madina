"""
Bootstrap Tests
===============

Tests the composition root (EventSystemFactory) and bootstrap.

ADR Reference: ADR-035
"""

import pytest

from backend.bootstrap.events import EventSystemFactory, EventSystemConfig, create_event_system
from backend.core.events import EventBusFacade, RoutingDestination


class TestEventSystemFactory:
    """Tests for EventSystemFactory."""

    def test_build_default(self):
        """Test building with default configuration."""
        factory = EventSystemFactory()
        facade = factory.build()

        assert isinstance(facade, EventBusFacade)
        assert facade.has_null_objects is False

    def test_build_with_routing_disabled(self):
        """Test building with routing disabled."""
        config = EventSystemConfig(enable_routing=False)
        factory = EventSystemFactory(config)
        facade = factory.build()

        assert isinstance(facade, EventBusFacade)
        # Null objects are used because routing is disabled
        assert facade.has_null_objects is True

    def test_build_with_custom_routing_rules(self):
        """Test building with custom routing rules."""
        config = EventSystemConfig(
            enable_routing=True,
            routing_rules={
                "order.created": RoutingDestination.WORKER,
                "payment.*": RoutingDestination.IMMEDIATE,
            },
        )
        factory = EventSystemFactory(config)
        facade = factory.build()

        assert isinstance(facade, EventBusFacade)

        # Verify routing works
        from backend.core.events import Job
        job = Job("order.created", {})
        decision = facade.route(job)
        assert decision.destination == RoutingDestination.WORKER

    def test_build_with_exponential_backoff(self):
        """Test building with exponential backoff retry."""
        config = EventSystemConfig(
            enable_retry=True,
            use_exponential_backoff=True,
            max_retry_attempts=5,
            retry_delay_ms=200,
            exponential_backoff_multiplier=2.0,
        )
        factory = EventSystemFactory(config)
        facade = factory.build()

        assert isinstance(facade, EventBusFacade)
        assert facade.get_max_retries() == 5

    def test_build_with_file_dead_letter(self):
        """Test building with file-based dead letter store."""
        config = EventSystemConfig(
            enable_dead_letter=True,
            dead_letter_filepath="test_dead_letter.json",
        )
        factory = EventSystemFactory(config)
        facade = factory.build()

        assert isinstance(facade, EventBusFacade)

    def test_build_disabled_dead_letter(self):
        """Test building with dead letter disabled."""
        config = EventSystemConfig(enable_dead_letter=False)
        factory = EventSystemFactory(config)
        facade = factory.build()

        assert isinstance(facade, EventBusFacade)
        assert facade.has_null_objects is True

    def test_factory_caching(self):
        """Test that factory caches the facade."""
        factory = EventSystemFactory()
        facade1 = factory.build()
        facade2 = factory.build()

        # Should return the same instance
        assert facade1 is facade2

    def test_create_event_system_convenience(self):
        """Test the convenience function."""
        facade = create_event_system()
        assert isinstance(facade, EventBusFacade)

    def test_invalid_config_raises(self):
        """Test that invalid config raises ValueError."""
        with pytest.raises(ValueError, match="max_retry_attempts must be >= 0"):
            config = EventSystemConfig(max_retry_attempts=-1)
            factory = EventSystemFactory(config)
            factory.build()