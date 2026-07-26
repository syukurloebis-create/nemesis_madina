"""
NEMESIS Madina - Fraud Events Tests
"""

import pytest
import json
from uuid import uuid4

from backend.domain.events.fraud_events import (
    FraudPattern,
    FraudPayload,
    FraudDetectionStarted,
    FraudDetectionCompleted,
)
from backend.domain.events.metadata import EventMetadata
from backend.domain.events.serialization import serialize, deserialize


class TestFraudEvents:
    def test_fraud_payload_to_dict(self):
        payload = FraudPayload(
            case_id=uuid4(),
            patterns=[
                FraudPattern(
                    type="COLLUSION",
                    severity="HIGH",
                    confidence=80.0,
                    validated=False,
                )
            ],
            overall_risk="CRITICAL",
            score=60.0,
            total_patterns=1,
            active_alerts=1,
            high_confidence=1,
            validated_patterns=0,
            highest_confidence=80.0,
            average_confidence=80.0,
        )
        
        data = payload.to_dict()
        assert data["overall_risk"] == "CRITICAL"
        assert data["score"] == 60.0
        assert len(data["patterns"]) == 1
    
    def test_fraud_payload_from_dict(self):
        original = FraudPayload(
            case_id=uuid4(),
            patterns=[],
            overall_risk="HIGH",
            score=50.0,
            total_patterns=0,
            active_alerts=0,
            high_confidence=0,
            validated_patterns=0,
            highest_confidence=0.0,
            average_confidence=0.0,
        )
        
        data = original.to_dict()
        restored = FraudPayload.from_dict(data)
        
        assert restored.case_id == original.case_id
        assert restored.overall_risk == original.overall_risk
        assert restored.score == original.score
    
    def test_fraud_detection_completed_event(self):
        metadata = EventMetadata.create(producer="fraud-engine")
        payload = FraudPayload(
            case_id=uuid4(),
            patterns=[],
            overall_risk="LOW",
            score=10.0,
            total_patterns=0,
            active_alerts=0,
            high_confidence=0,
            validated_patterns=0,
            highest_confidence=0.0,
            average_confidence=0.0,
        )
                
        event = FraudDetectionCompleted(metadata=metadata, payload=payload)
        
        assert FraudDetectionCompleted.EVENT_NAME == "FraudDetectionCompleted"
        assert event.event_name == "FraudDetectionCompleted"
        assert event.metadata.producer == "fraud-engine"
        
        data = event.to_dict()
        assert data["event_name"] == "FraudDetectionCompleted"
        assert data["payload"]["overall_risk"] == "LOW"