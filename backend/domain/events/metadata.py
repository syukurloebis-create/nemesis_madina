"""
NEMESIS Madina - Event Metadata
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Any, Dict

from backend.domain.value_objects import (
    EventId,
    TraceId,
    CorrelationId,
    TenantId,
    AggregateId,
)
from backend.domain.enums.classification import DataClassification


@dataclass(frozen=True)
class EventMetadata:
    """Immutable metadata for all events."""
    
    event_id: EventId
    correlation_id: Optional[CorrelationId] = None
    causation_id: Optional[EventId] = None
    trace_id: Optional[TraceId] = None
    tenant_id: Optional[TenantId] = None
    aggregate_id: Optional[AggregateId] = None
    aggregate_type: Optional[str] = None
    aggregate_version: Optional[int] = None
    event_version: str = "1.0"
    schema_version: str = "1.0"
    producer: str = "unknown"
    classification: DataClassification = DataClassification.INTERNAL
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def create(
        cls,
        aggregate_id: Optional[AggregateId] = None,
        aggregate_type: Optional[str] = None,
        producer: str = "unknown",
        classification: DataClassification = DataClassification.INTERNAL,
        correlation_id: Optional[CorrelationId] = None,
        causation_id: Optional[EventId] = None,
        trace_id: Optional[TraceId] = None,
        tenant_id: Optional[TenantId] = None,
        event_version: str = "1.0",
    ) -> "EventMetadata":
        """Factory method for creating metadata with defaults."""
        return cls(
            event_id=EventId.generate(),
            correlation_id=correlation_id,
            causation_id=causation_id,
            trace_id=trace_id,
            tenant_id=tenant_id,
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            aggregate_version=None,
            event_version=event_version,
            schema_version="1.0",
            producer=producer,
            classification=classification,
            occurred_at=datetime.now(timezone.utc),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "event_id": str(self.event_id),
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
            "causation_id": str(self.causation_id) if self.causation_id else None,
            "trace_id": str(self.trace_id) if self.trace_id else None,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "aggregate_id": str(self.aggregate_id) if self.aggregate_id else None,
            "aggregate_type": self.aggregate_type,
            "aggregate_version": self.aggregate_version,
            "event_version": self.event_version,
            "schema_version": self.schema_version,
            "producer": self.producer,
            "classification": self.classification.value,
            "occurred_at": self.occurred_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventMetadata":
        """Create from dict."""
        return cls(
            event_id=EventId.from_string(data["event_id"]),
            correlation_id=CorrelationId.from_string(data["correlation_id"]) if data.get("correlation_id") else None,
            causation_id=EventId.from_string(data["causation_id"]) if data.get("causation_id") else None,
            trace_id=TraceId.from_string(data["trace_id"]) if data.get("trace_id") else None,
            tenant_id=TenantId.from_string(data["tenant_id"]) if data.get("tenant_id") else None,
            aggregate_id=AggregateId.from_string(data["aggregate_id"]) if data.get("aggregate_id") else None,
            aggregate_type=data.get("aggregate_type"),
            aggregate_version=data.get("aggregate_version"),
            event_version=data.get("event_version", "1.0"),
            schema_version=data.get("schema_version", "1.0"),
            producer=data.get("producer", "unknown"),
            classification=DataClassification(data.get("classification", "INTERNAL")),
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
        )