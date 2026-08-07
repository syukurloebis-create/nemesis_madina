"""
Unit Tests for Retry Components
===============================

Tests the DefaultRetryPolicy and ExponentialBackoffRetryPolicy implementations.
"""

import pytest
from datetime import datetime, timezone

from backend.core.events import BaseEvent, DefaultRetryPolicy, ExponentialBackoffRetryPolicy
from backend.core.events.interfaces.retry import FailureClassification, RetryDecision


class TestDefaultRetryPolicy:
    """Tests for DefaultRetryPolicy."""

    @pytest.fixture
    def event(self):
        return BaseEvent(event_type="test.event", _payload={})

    def test_evaluate_retry_on_recoverable(self, event):
        policy = DefaultRetryPolicy(max_attempts=3)
        decision = policy.evaluate(event, 0, ConnectionError("Network error"))

        assert decision.should_retry is True
        assert decision.delay_ms == 100

    def test_evaluate_no_retry_on_permanent(self, event):
        policy = DefaultRetryPolicy(max_attempts=3)
        decision = policy.evaluate(event, 0, ValueError("Invalid data"))

        assert decision.should_retry is False

    def test_evaluate_no_retry_on_max_attempts(self, event):
        policy = DefaultRetryPolicy(max_attempts=3)
        decision = policy.evaluate(event, 3, ConnectionError("Network error"))

        assert decision.should_retry is False
        assert "Max attempts" in decision.reason

    def test_evaluate_custom_delay(self, event):
        policy = DefaultRetryPolicy(max_attempts=3, delay_ms=500)
        decision = policy.evaluate(event, 0, ConnectionError("Network error"))

        assert decision.should_retry is True
        assert decision.delay_ms == 500

    def test_classify_failure_recoverable(self):
        policy = DefaultRetryPolicy()
        classification = policy.classify_failure(ConnectionError("Network error"))
        assert classification == FailureClassification.RECOVERABLE

    def test_classify_failure_programming(self):
        policy = DefaultRetryPolicy()
        classification = policy.classify_failure(ValueError("Invalid value"))
        assert classification == FailureClassification.PROGRAMMING

    def test_classify_failure_configuration(self):
        policy = DefaultRetryPolicy()
        classification = policy.classify_failure(Exception("config error"))
        assert classification == FailureClassification.CONFIGURATION

    def test_get_max_attempts(self):
        policy = DefaultRetryPolicy(max_attempts=5)
        assert policy.get_max_attempts() == 5

    def test_evaluate_raises_on_invalid_event(self):
        policy = DefaultRetryPolicy()
        with pytest.raises(ValueError, match="event cannot be None"):
            policy.evaluate(None, 0, Exception("fail"))

    def test_evaluate_raises_on_invalid_attempt(self):
        policy = DefaultRetryPolicy()
        event = BaseEvent(event_type="test.event", _payload={})
        with pytest.raises(ValueError, match="attempt must be >= 0"):
            policy.evaluate(event, -1, Exception("fail"))


class TestExponentialBackoffRetryPolicy:
    """Tests for ExponentialBackoffRetryPolicy."""

    @pytest.fixture
    def event(self):
        return BaseEvent(event_type="test.event", _payload={})

    def test_exponential_backoff_delay(self, event):
        policy = ExponentialBackoffRetryPolicy(
            max_attempts=3,
            base_delay_ms=100,
            multiplier=2.0,
        )

        # Attempt 0: 100ms
        decision = policy.evaluate(event, 0, ConnectionError("fail"))
        assert decision.should_retry is True
        assert 80 <= decision.delay_ms <= 120  # Allow for jitter

        # Attempt 1: 200ms
        decision = policy.evaluate(event, 1, ConnectionError("fail"))
        assert decision.should_retry is True
        assert 160 <= decision.delay_ms <= 240

        # Attempt 2: 400ms
        decision = policy.evaluate(event, 2, ConnectionError("fail"))
        assert decision.should_retry is True
        assert 320 <= decision.delay_ms <= 480

    def test_exponential_backoff_max_delay(self, event):
        policy = ExponentialBackoffRetryPolicy(
            max_attempts=5,
            base_delay_ms=100,
            multiplier=2.0,
            max_delay_ms=500,
        )

        # Attempt 3: should be capped at 500ms
        decision = policy.evaluate(event, 3, ConnectionError("fail"))
        assert decision.should_retry is True
        assert decision.delay_ms <= 500

    def test_exponential_backoff_no_jitter(self, event):
        policy = ExponentialBackoffRetryPolicy(
            max_attempts=3,
            base_delay_ms=100,
            multiplier=2.0,
            jitter=False,
        )

        decision = policy.evaluate(event, 0, ConnectionError("fail"))
        assert decision.delay_ms == 100

        decision = policy.evaluate(event, 1, ConnectionError("fail"))
        assert decision.delay_ms == 200