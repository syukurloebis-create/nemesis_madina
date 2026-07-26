"""
NEMESIS Madina - Evidence Events Tests
"""

import pytest
from uuid import uuid4

from backend.domain.events.evidence_events import EvidencePayload, EvidenceVerificationCompleted
from backend.domain.events.metadata import EventMetadata


class TestEvidenceEvents:
    def test_evidence_payload_to_dict(self):
        payload = EvidencePayload(
            case_id=uuid4(),
            score=41.98,
            level="MEDIUM",
            total=9,
            verified=5,
            rejected=4,
            pending=0,
            avg_trust=70.22,
            avg_confidence=0.0,
            confidence_level="UNKNOWN",
        )
        
        data = payload.to_dict()
        assert data["score"] == 41.98
        assert data["level"] == "MEDIUM"
        assert data["total"] == 9
        assert data["verified"] == 5