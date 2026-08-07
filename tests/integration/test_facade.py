"""
Integration Tests for EventBusFacade
====================================

End-to-end tests for the complete event flow.

ADR Reference: ADR-035
"""

import pytest
import asyncio

from backend.bootstrap.events import EventSystemFactory, EventSystemConfig, EventSystemFactory
from backend.core.events import BaseEvent, RoutingDestination, EventBusFacade


class TestEventBusFacadeIntegration:
    """Integration tests for EventBusFacade."""

    @pytest.fixture
    def facade(self):
        """Create a fully assembled facade for testing."""
        # Reset singleton for testing
        EventSystemFactory.reset()
        
        config = EventSystemConfig(
            enable_routing=True,
            enable_retry=True,
            enable_dead_letter=True,
            routing_rules={
                "test.event": RoutingDestination.IMMEDIATE,
            },
        )
        factory = EventSystemFactory(config)
        return factory.build()

    @pytest.fixture
    def event(self):
        """Create a test event."""
        return BaseEvent(
            event_type="test.event",
            _payload={"message": "Hello, World!"},
        )

    @pytest.mark.asyncio
    async def test_publish_and_subscribe(self, facade, event):
        """Test publishing and subscribing to events."""
        received_events = []

        async def handler(e):
            received_events.append(e)

        # Subscribe
        facade.subscribe("test.event", handler)

        # Publish
        await facade.publish(event)

        # Give time for async processing
        await asyncio.sleep(0.5)

        assert len(received_events) == 1, f"Expected 1 event, got {len(received_events)}"
        assert received_events[0].event_id == event.event_id

    @pytest.mark.asyncio
    async def test_publish_with_correlation(self, facade, event):
        """Test publishing with correlation ID."""
        received_events = []

        async def handler(e):
            received_events.append(e)

        facade.subscribe("test.event", handler)

        correlation_id = "test-correlation-123"
        await facade.publish_with_correlation(event, correlation_id)

        await asyncio.sleep(0.5)

        assert len(received_events) == 1, f"Expected 1 event, got {len(received_events)}"

    def test_route(self, facade):
        """Test routing a job."""
        from backend.core.events import Job

        job = Job("test.event", {})
        decision = facade.route(job)

        assert decision.destination == RoutingDestination.IMMEDIATE

    def test_retry_policy(self, facade, event):
        """Test retry policy."""
        decision = facade.evaluate_retry(event, 0, ConnectionError("Network error"))

        assert decision.should_retry is True

        # Max attempts exceeded
        decision = facade.evaluate_retry(event, 3, ConnectionError("Network error"))

        assert decision.should_retry is False

    def test_dead_letter(self, facade, event):
        """Test dead letter store."""
        from backend.core.events.interfaces.dead_letter import DeadLetterEntry

        # Store
        entry = DeadLetterEntry(
            event=event,
            failure_reason="Test failure",
            failure_type="TEST",
            attempts=3,
        )
        facade.store_dead_letter(entry)

        # Count
        assert facade.count_dead_letters() == 1

        # Get all
        entries = facade.get_dead_letters()
        assert len(entries) == 1

        # Get by ID
        retrieved = facade.get_dead_letter(event.event_id)
        assert retrieved is not None

        # Replay
        assert facade.replay_dead_letter(event.event_id) is True

        # Remove
        assert facade.remove_dead_letter(event.event_id) is True
        assert facade.count_dead_letters() == 0

    @pytest.mark.asyncio
    async def test_full_flow_with_retry(self, facade, event):
        """Test full flow: publish → retry → dead letter."""
        attempts = []

        async def failing_handler(e):
            attempts.append(1)
            raise ConnectionError("Simulated network failure")

        # Subscribe a failing handler
        facade.subscribe("test.event", failing_handler)

        # Publish
        await facade.publish(event)

        # Give time for processing (max attempts = 3)
        await asyncio.sleep(0.5)

        # The event should have been retried and then dead-lettered
        assert len(attempts) >= 3, f"Expected at least 3 attempts, got {len(attempts)}"

        # Check dead letter
        assert facade.count_dead_letters() >= 1

        entry = facade.get_dead_letter(event.event_id)
        if entry is not None:
            assert "Max attempts" in entry.failure_reason or "exceeded" in entry.failure_reason