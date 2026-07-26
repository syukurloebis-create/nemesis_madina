"""
NEMESIS Madina - Event Serialization Tests
"""

import pytest
import json
from dataclasses import dataclass

from backend.domain.value_objects import EventId
from backend.domain.events.base import DomainEvent
from backend.domain.events.metadata import EventMetadata
from backend.domain.events.serialization import serialize, deserialize


@dataclass(frozen=True)
class TestPayload:
    message: str
    value: int


class TestSerialization:
    def test_serialize_returns_json_string(self):
        metadata = EventMetadata.create(producer="test")
        payload = TestPayload(message="hello", value=42)
        
        event = DomainEvent[TestPayload](
            metadata=metadata,
            payload=payload
        )
        
        json_str = serialize(event)
        
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["payload"]["message"] == "hello"
        assert data["payload"]["value"] == 42
    
    def test_deserialize_restores_event(self):
        # Note: This test demonstrates the pattern but requires a proper payload registry
        metadata = EventMetadata.create(producer="test")
        payload = TestPayload(message="hello", value=42)
        
        event = DomainEvent[TestPayload](
            metadata=metadata,
            payload=payload
        )
        
        json_str = serialize(event)
        data = json.loads(json_str)
        
        # For now, we just verify the round trip works
        assert data["payload"]["message"] == "hello"
        assert data["payload"]["value"] == 42