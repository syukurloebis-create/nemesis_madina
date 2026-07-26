"""
NEMESIS Madina - Procurement Events Tests
"""

import pytest
from uuid import uuid4

from backend.domain.events.procurement_events import ProcurementPayload, ProcurementAnalysisCompleted
from backend.domain.events.metadata import EventMetadata


class TestProcurementEvents:
    def test_procurement_payload_to_dict(self):
        payload = ProcurementPayload(
            case_id=uuid4(),
            packages=3630,
            vendors=549,
            instansi_count=1,
            total_value=583974259200.0,
            avg_value=160918781.81,
            completed=0,
        )
        
        data = payload.to_dict()
        assert data["packages"] == 3630
        assert data["vendors"] == 549
        assert data["total_value"] == 583974259200.0