"""
Unit Tests for Dead Letter Components
=====================================

Tests the InMemoryDeadLetterStore implementation.
"""

import pytest
from datetime import datetime, timezone

from backend.core.events import BaseEvent, InMemoryDeadLetterStore
from backend.core.events.interfaces.dead_letter import DeadLetterEntry


class TestInMemoryDeadLetterStore:
    """Tests for InMemoryDeadLetterStore."""

    @pytest.fixture
    def store(self):
        return InMemoryDeadLetterStore()

    @pytest.fixture
    def event(self):
        return BaseEvent(event_type="test.event", _payload={"key": "value"})

    @pytest.fixture
    def entry(self, event):
        return DeadLetterEntry(
            event=event,
            failure_reason="Test failure",
            failure_type="TEST",
            attempts=3,
        )

    def test_store(self, store, entry):
        store.store(entry)
        assert store.count() == 1

    def test_get_all(self, store, entry):
        store.store(entry)
        entries = store.get_all()
        assert len(entries) == 1
        assert entries[0].event.event_id == entry.event.event_id

    def test_get_by_event_id(self, store, entry):
        store.store(entry)
        retrieved = store.get_by_event_id(entry.event.event_id)
        assert retrieved is not None
        assert retrieved.event.event_id == entry.event.event_id

    def test_get_by_event_id_not_found(self, store):
        retrieved = store.get_by_event_id("non-existent-id")
        assert retrieved is None

    def test_replay(self, store, entry):
        store.store(entry)
        assert store.replay(entry.event.event_id) is True

    def test_replay_not_found(self, store):
        assert store.replay("non-existent-id") is False

    def test_remove(self, store, entry):
        store.store(entry)
        assert store.remove(entry.event.event_id) is True
        assert store.count() == 0

    def test_remove_not_found(self, store):
        assert store.remove("non-existent-id") is False

    def test_count(self, store, entry):
        assert store.count() == 0
        store.store(entry)
        assert store.count() == 1
        store.store(entry)  # Same event ID will overwrite
        assert store.count() == 1

    def test_clear(self, store, entry):
        store.store(entry)
        assert store.count() == 1
        store.clear()
        assert store.count() == 0

    def test_store_raises_on_invalid_entry(self, store):
        with pytest.raises(ValueError, match="entry cannot be None"):
            store.store(None)

    def test_store_raises_on_invalid_event(self, store):
        entry = DeadLetterEntry(
            event=None,  # type: ignore
            failure_reason="Test",
            failure_type="TEST",
            attempts=1,
        )
        with pytest.raises(ValueError, match="entry.event cannot be None"):
            store.store(entry)