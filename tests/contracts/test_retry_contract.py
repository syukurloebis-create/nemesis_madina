"""
Contract Tests for IEventRetryPolicy
====================================

Verifies that retry implementations satisfy the IEventRetryPolicy contract.

ADR Reference: ADR-033
"""

import pytest

from backend.core.events import BaseEvent, DefaultRetryPolicy, ExponentialBackoffRetryPolicy
from backend.core.events.interfaces.retry import IEventRetryPolicy, RetryDecision


class TestIEventRetryPolicyContract:
    """Contract tests for IEventRetryPolicy implementations."""

    @pytest.fixture
    def policies(self):
        return [
            DefaultRetryPolicy(),
            ExponentialBackoffRetryPolicy(),
        ]

    @pytest.fixture
    def event(self):
        return BaseEvent(event_type="test.event", _payload={})

    def test_evaluate_returns_retry_decision(self, policies, event):
        for policy in policies:
            decision = policy.evaluate(event, 0, Exception("Test error"))
            assert isinstance(decision, RetryDecision)

    def test_get_max_attempts_returns_int(self, policies):
        for policy in policies:
            assert isinstance(policy.get_max_attempts(), int)

    def test_classify_failure_returns_classification(self, policies):
        for policy in policies:
            classification = policy.classify_failure(Exception("Test error"))
            from backend.core.events.interfaces.retry import FailureClassification
            assert classification in FailureClassification

    def test_evaluate_raises_on_invalid_event(self, policies):
        for policy in policies:
            with pytest.raises(ValueError):
                policy.evaluate(None, 0, Exception("fail"))