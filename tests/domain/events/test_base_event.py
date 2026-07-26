"""
NEMESIS Madina - DomainEvent Tests
"""

import pytest
from dataclasses import dataclass

from backend.domain.value_objects import EventId
from backend.domain.events.base import DomainEvent
from backend.domain.events.metadata import EventMetadata


@dataclass(frozen=True)
class TestPayload:
    message: str
    value: int


class TestDomainEvent:
    def test_event_has_metadata_and_payload(self):
        metadata = EventMetadata.create(producer="test")
        payload = TestPayload(message="hello", value=42)
        
        event = DomainEvent[TestPayload](
            metadata=metadata,
            payload=payload
        )
        
        assert event.metadata == metadata
        assert event.payload == payload
    
    def test_to_dict_serializes(self):
        metadata = EventMetadata.create(producer="test")
        payload = TestPayload(message="hello", value=42)
        
        event = DomainEvent[TestPayload](
            metadata=metadata,
            payload=payload
        )
        
        data = event.to_dict()
        
        assert "metadata" in data
        assert "payload" in data
        assert data["payload"]["message"] == "hello"
        assert data["payload"]["value"] == 42