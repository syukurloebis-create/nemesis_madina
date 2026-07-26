"""
NEMESIS Madina - EventMetadata Tests
"""

import pytest
from datetime import datetime, timezone

from backend.domain.value_objects import EventId, TraceId, CorrelationId, TenantId, AggregateId
from backend.domain.enums.classification import DataClassification
from backend.domain.events.metadata import EventMetadata


class TestEventMetadata:
    def test_create_factory_sets_defaults(self):
        metadata = EventMetadata.create(
            producer="test-service",
            classification=DataClassification.CONFIDENTIAL
        )
        
        assert metadata.event_id is not None
        assert metadata.producer == "test-service"
        assert metadata.classification == DataClassification.CONFIDENTIAL
        assert metadata.schema_version == "1.0"
        assert metadata.event_version == "1.0"
        assert metadata.aggregate_version is None
    
    def test_create_with_aggregate(self):
        aggregate_id = AggregateId.generate()
        metadata = EventMetadata.create(
            aggregate_id=aggregate_id,
            aggregate_type="TestAggregate",
            producer="test-service"
        )
        
        assert metadata.aggregate_id == aggregate_id
        assert metadata.aggregate_type == "TestAggregate"
    
    def test_to_dict_serializes_correctly(self):
        metadata = EventMetadata.create(
            producer="test-service",
            classification=DataClassification.INTERNAL
        )
        
        data = metadata.to_dict()
        
        assert "event_id" in data
        assert "producer" in data
        assert data["producer"] == "test-service"
        assert data["classification"] == "INTERNAL"
        assert "occurred_at" in data
    
    def test_from_dict_deserializes_correctly(self):
        original = EventMetadata.create(
            producer="test-service",
            classification=DataClassification.CONFIDENTIAL
        )
        
        data = original.to_dict()
        restored = EventMetadata.from_dict(data)
        
        assert restored.event_id == original.event_id
        assert restored.producer == original.producer
        assert restored.classification == original.classification
        assert restored.occurred_at == original.occurred_at