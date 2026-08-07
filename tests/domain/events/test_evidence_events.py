"""
NEMESIS Madina - Evidence Events Tests
"""

import pytest
from uuid import uuid4

from backend.domain.value_objects.case_id import CaseId
from backend.domain.events.evidence_events import EvidencePayload, EvidenceVerificationCompleted
from backend.domain.events.metadata import EventMetadata


class TestEvidenceEvents:
    def test_evidence_payload_to_dict(self):
        payload = EvidencePayload(
            case_id=CaseId(str(uuid4())),
            verified_count=5,
            pending_count=0,
            rejected_count=4,
            total_count=9,
            score=41.98,
        )

        data = payload.to_dict()
        assert data["verified_count"] == 5
        assert data["pending_count"] == 0
        assert data["rejected_count"] == 4
        assert data["total_count"] == 9
        assert data["score"] == 41.98