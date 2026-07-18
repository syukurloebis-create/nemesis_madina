# backend/domain/events/procurement_events.py
"""
NEMESIS Madina - Procurement Domain Events
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from uuid import UUID

from backend.domain.events.base import DomainEvent
from backend.domain.value_objects.procurement_analysis import ProcurementAnalysis
from backend.domain.value_objects.case_id import CaseId


@dataclass(frozen=True)
class ProcurementPayload:
    """New-style payload for procurement events."""
    
    case_id: CaseId
    total_spend: float
    vendor_count: int
    transaction_count: int
    flagged_transactions: int
    high_risk_vendors: int
    duplicate_invoices: int
    irregular_patterns: List[Dict[str, Any]]
    fraud_indicators: List[str]
    risk_score: float
    confidence: float
    status: str = "SUCCESS"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": str(self.case_id),
            "total_spend": self.total_spend,
            "vendor_count": self.vendor_count,
            "transaction_count": self.transaction_count,
            "flagged_transactions": self.flagged_transactions,
            "high_risk_vendors": self.high_risk_vendors,
            "duplicate_invoices": self.duplicate_invoices,
            "irregular_patterns": self.irregular_patterns,
            "fraud_indicators": self.fraud_indicators,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcurementPayload":
        return cls(
            case_id=CaseId(data["case_id"]),
            total_spend=data["total_spend"],
            vendor_count=data["vendor_count"],
            transaction_count=data["transaction_count"],
            flagged_transactions=data["flagged_transactions"],
            high_risk_vendors=data["high_risk_vendors"],
            duplicate_invoices=data["duplicate_invoices"],
            irregular_patterns=data["irregular_patterns"],
            fraud_indicators=data["fraud_indicators"],
            risk_score=data["risk_score"],
            confidence=data["confidence"],
            status=data.get("status", "SUCCESS"),
        )


@dataclass(frozen=True)
class ProcurementAnalysisCompleted(DomainEvent[ProcurementPayload]):
    EVENT_NAME = "ProcurementAnalysisCompleted"
    EVENT_VERSION = "1"


# ============================================================================
# COMPATIBILITY ADAPTER (Plain Class)
# ============================================================================

class ProcurementAnalysisPerformed(ProcurementAnalysisCompleted):
    """Compatibility adapter for old aggregate calls."""
    
    def __init__(self, case_id: CaseId, analysis: ProcurementAnalysis):
        payload = ProcurementPayload(
            case_id=case_id,
            total_spend=analysis.total_spend,
            vendor_count=analysis.vendor_count,
            transaction_count=analysis.transaction_count,
            flagged_transactions=analysis.flagged_transactions,
            high_risk_vendors=analysis.high_risk_vendors,
            duplicate_invoices=analysis.duplicate_invoices,
            irregular_patterns=analysis.irregular_patterns,
            fraud_indicators=analysis.fraud_indicators,
            risk_score=analysis.risk_score,
            confidence=analysis.confidence,
        )
        super().__init__(payload=payload)