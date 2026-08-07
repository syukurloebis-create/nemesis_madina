"""
NEMESIS Madina - Procurement Events Tests
"""

import pytest
from uuid import uuid4

from backend.domain.events.procurement_events import ProcurementPayload, ProcurementAnalysisCompleted
from backend.domain.events.metadata import EventMetadata
from backend.domain.value_objects.case_id import CaseId


class TestProcurementEvents:
    def test_procurement_payload_to_dict(self):
        payload = ProcurementPayload(
            case_id=CaseId(str(uuid4())),
            total_spend=583974259200.0,
            vendor_count=549,
            transaction_count=3630,
            flagged_transactions=0,
            high_risk_vendors=0,
            duplicate_invoices=0,
            irregular_patterns=[],
            fraud_indicators=[],
            risk_score=0.0,
            confidence=0.0,
            status="SUCCESS",
        )

        data = payload.to_dict()
        assert data["total_spend"] == 583974259200.0
        assert data["vendor_count"] == 549
        assert data["transaction_count"] == 3630