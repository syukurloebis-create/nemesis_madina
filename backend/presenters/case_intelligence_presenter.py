"""
Case Intelligence Presenter — Convert CaseIntelligence to Dict.
"""

from typing import Dict, Any, List, Optional

from backend.domain.models.case_intelligence import CaseIntelligence
from backend.presenters.summary_presenter import SummaryPresenter


class CaseIntelligencePresenter:
    """
    Case Intelligence Presenter — Convert Aggregate to Dict.
    """

    @staticmethod
    def to_dict(case_intel: CaseIntelligence) -> Dict[str, Any]:
        """Convert CaseIntelligence to dict."""
        return {
            "case_id": case_intel.case_id,
            "total": case_intel.total,
            "critical": case_intel.critical,
            "high": case_intel.high,
            "medium": case_intel.medium,
            "findings": case_intel.findings or [],
            "fraud": SummaryPresenter.fraud_to_dict(case_intel.fraud),
            "graph": SummaryPresenter.graph_to_dict(case_intel.graph),
            "risk": SummaryPresenter.risk_to_dict(case_intel.risk),
            "evidence": SummaryPresenter.evidence_to_dict(case_intel.evidence),
            "procurement": SummaryPresenter.procurement_to_dict(case_intel.procurement),
            "recovery": SummaryPresenter.recovery_to_dict(case_intel.recovery),
            "confidence": case_intel.confidence,
            "status": case_intel.status,
            "generated_at": case_intel.generated_at.isoformat() if case_intel.generated_at else None,
            "request_id": case_intel.request_id,
            "trace_id": case_intel.trace_id,
            "version": case_intel.version
        }