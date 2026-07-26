"""
NEMESIS Madina - Application Events Tests
"""

import pytest
from uuid import uuid4

from backend.domain.events.application_events import (
    IntelligenceAssessmentPayload,
    IntelligenceAssessmentCompleted,
)
from backend.domain.events.metadata import EventMetadata


class TestApplicationEvents:
    def test_intelligence_assessment_payload_to_dict(self):
        payload = IntelligenceAssessmentPayload(
            case_id=uuid4(),
            status="operational",
            confidence=44.63,
            version="1.0",
            duration_ms=1234.56,
        )
        
        data = payload.to_dict()
        assert data["status"] == "operational"
        assert data["confidence"] == 44.63
        assert data["duration_ms"] == 1234.56
    
    def test_intelligence_assessment_completed_event(self):
        metadata = EventMetadata.create(producer="intelligence-orchestrator")
        payload = IntelligenceAssessmentPayload(
            case_id=uuid4(),
            status="operational",
            confidence=50.0,
            version="1.0",
            duration_ms=500.0,
        )
        
        event = IntelligenceAssessmentCompleted(metadata=metadata, payload=payload)

        assert IntelligenceAssessmentCompleted.EVENT_NAME == "IntelligenceAssessmentCompleted"
        assert event.event_name == "IntelligenceAssessmentCompleted"
        assert event.metadata.producer == "intelligence-orchestrator"