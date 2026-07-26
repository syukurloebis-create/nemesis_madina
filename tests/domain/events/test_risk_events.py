"""
NEMESIS Madina - Risk Events Tests
"""

import pytest
from uuid import uuid4

from backend.domain.events.risk_events import RiskPayload, RiskAssessmentCompleted
from backend.domain.events.metadata import EventMetadata


class TestRiskEvents:
    def test_risk_payload_to_dict(self):
        payload = RiskPayload(
            case_id=uuid4(),
            score=75.0,
            level="HIGH",
            anomaly_score=60.0,
            collusion_score=80.0,
            financial_score=50.0,
        )
        
        data = payload.to_dict()
        assert data["score"] == 75.0
        assert data["level"] == "HIGH"
    
    def test_risk_payload_from_dict(self):
        original = RiskPayload(
            case_id=uuid4(),
            score=45.0,
            level="MEDIUM",
            anomaly_score=30.0,
            collusion_score=50.0,
            financial_score=40.0,
        )
        
        data = original.to_dict()
        restored = RiskPayload.from_dict(data)
        
        assert restored.case_id == original.case_id
        assert restored.score == original.score
        assert restored.level == original.level