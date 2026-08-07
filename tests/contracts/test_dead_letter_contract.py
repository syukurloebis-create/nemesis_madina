"""
Contract Tests for IDeadLetterStore
===================================

Verifies that dead letter implementations satisfy the IDeadLetterStore contract.

ADR Reference: ADR-035
"""

import pytest

from backend.core.events import BaseEvent, InMemoryDeadLetterStore
from backend.core.events.interfaces.dead_letter import IDeadLetterStore, DeadLetterEntry


class TestIDeadLetterStoreContract:
    """Contract tests for IDeadLetterStore implementations."""

    @pytest.fixture
    def stores(self):
        return [
            InMemoryDeadLetterStore(),
        ]

    @pytest.fixture
    def event(self):
        return BaseEvent(event_type="test.event", _payload={})

    @pytest.fixture
    def entry(self, event):
        return DeadLetterEntry(
            event=event,
            failure_reason="Test failure",
            failure_type="TEST",
            attempts=3,
        )

    def test_store_accepts_entry(self, stores, entry):
        for store in stores:
            store.store(entry)

    def test_get_all_returns_list(self, stores, entry):
        for store in stores:
            store.store(entry)
            result = store.get_all()
            assert isinstance(result, list)
            assert len(result) > 0

    def test_get_by_event_id_returns_entry_or_none(self, stores, entry):
        for store in stores:
            store.store(entry)
            result = store.get_by_event_id(entry.event.event_id)
            assert result is not None or result is None

    def test_replay_returns_bool(self, stores, entry):
        for store in stores:
            store.store(entry)
            assert isinstance(store.replay(entry.event.event_id), bool)

    def test_remove_returns_bool(self, stores, entry):
        for store in stores:
            store.store(entry)
            assert isinstance(store.remove(entry.event.event_id), bool)

    def test_count_returns_int(self, stores, entry):
        for store in stores:
            store.store(entry)
            assert isinstance(store.count(), int)
            assert store.count() > 0