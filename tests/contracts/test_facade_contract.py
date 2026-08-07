"""
Contract Tests for EventBusFacade
=================================

Verifies that EventBusFacade satisfies the contract.

ADR Reference: ADR-035
"""

import pytest

from backend.core.events import EventBusFacade, BaseEvent, Job, RoutingDecision
from backend.core.events.null_objects import (
    NullEventRouter,
    NullEventRetryPolicy,
    NullDeadLetterStore,
)


class TestEventBusFacadeContract:
    """Contract tests for EventBusFacade."""

    @pytest.fixture
    def facade(self):
        """Create a facade with null objects for testing."""
        class MockPublisher:
            async def publish(self, event): pass
            async def publish_with_correlation(self, event, correlation_id=None): pass

        class MockSubscriber:
            def subscribe(self, event_type, handler): pass
            def unsubscribe(self, event_type, handler): pass
            def get_handlers(self, event_type): return []

        return EventBusFacade(
            publisher=MockPublisher(),
            subscriber=MockSubscriber(),
            router=NullEventRouter(),
            retry_policy=NullEventRetryPolicy(),
            dead_letter_store=NullDeadLetterStore(),
            use_null_objects=False,
        )

    def test_route_returns_routing_decision(self, facade):
        """Test that route returns a RoutingDecision."""
        job = Job("test.event", {})
        decision = facade.route(job)
        assert isinstance(decision, RoutingDecision)

    def test_retry_policy_returns_decision(self, facade):
        """Test that retry policy returns a RetryDecision."""
        event = BaseEvent(event_type="test.event", _payload={})
        decision = facade.evaluate_retry(event, 0, Exception("fail"))
        from backend.core.events import RetryDecision
        assert isinstance(decision, RetryDecision)

    def test_dead_letter_returns_count(self, facade):
        """Test that dead letter store returns a count."""
        count = facade.count_dead_letters()
        assert isinstance(count, int)
        assert count >= 0

    def test_get_max_retries_returns_int(self, facade):
        """Test that get_max_retries returns an int."""
        max_retries = facade.get_max_retries()
        assert isinstance(max_retries, int)
        assert max_retries >= 0