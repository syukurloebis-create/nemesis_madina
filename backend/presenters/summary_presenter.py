"""
Summary Presenter — Convert Domain Models to Dict/JSON.

Architecture Decision:
- Presenter hanya untuk formatting response
- HANYA mapping, TIDAK ada business logic
- Domain models dari summary_objects.py
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.domain.summary_objects import (
    FraudSummary,
    GraphSummary,
    RiskSummary,
    EvidenceSummary,
    ProcurementSummary,
    RecoverySummary,
    DashboardSummary
)


class SummaryPresenter:
    """
    Summary Presenter — Convert Domain to Dict.
    
    NOTE: CollusionSummary telah dihapus dari arsitektur baru.
    Semua referensi ke CollusionSummary telah dihapus.
    """

    @staticmethod
    def fraud_to_dict(fraud: FraudSummary) -> Dict[str, Any]:
        """Convert FraudSummary to dict."""
        return {
            "overall_risk": fraud.overall_risk.value if fraud.overall_risk else "UNKNOWN",
            "score": fraud.score,
            "total_patterns": fraud.total_patterns,
            "active_alerts": fraud.active_alerts,
            "high_confidence": fraud.high_confidence,
            "validated_patterns": fraud.validated_patterns,
            "highest_confidence": fraud.highest_confidence,
            "average_confidence": fraud.average_confidence,
            "signals": fraud.signals or {},
            "engine": fraud.engine.value if hasattr(fraud.engine, "value") else str(fraud.engine),
            "engine_status": fraud.engine_status.value if fraud.engine_status else "OK"
        }

    @staticmethod
    def graph_to_dict(graph: GraphSummary) -> Dict[str, Any]:
        """Convert GraphSummary to dict."""
        return {
            "entities": graph.entities,
            "relationships": graph.relationships,
            "engine": graph.engine.value if hasattr(graph.engine, "value") else str(graph.engine),
            "engine_status": graph.engine_status.value if graph.engine_status else "OK"
        }

    @staticmethod
    def risk_to_dict(risk: RiskSummary) -> Dict[str, Any]:
        """Convert RiskSummary to dict."""
        return {
            "score": risk.score,
            "level": risk.level.value if risk.level else "UNKNOWN",
            "status": risk.status,
            "anomaly_score": risk.anomaly_score,
            "collusion_score": risk.collusion_score,
            "financial_score": risk.financial_score,
            "recommendations": risk.recommendations or [],
            "engine": risk.engine.value if hasattr(risk.engine, "value") else str(risk.engine),
            "engine_status": risk.engine_status.value if risk.engine_status else "OK"
        }

    @staticmethod
    def evidence_to_dict(evidence: EvidenceSummary) -> Dict[str, Any]:
        """Convert EvidenceSummary to dict."""
        return {
            "score": evidence.score,
            "level": evidence.level.value if evidence.level else "NO_DATA",
            "total": evidence.total,
            "verified": evidence.verified,
            "rejected": evidence.rejected,
            "pending": evidence.pending,
            "avg_trust": evidence.avg_trust,
            "avg_confidence": evidence.avg_confidence,
            "confidence_level": evidence.confidence_level,
            "engine": evidence.engine.value if hasattr(evidence.engine, "value") else str(evidence.engine),
            "engine_status": evidence.engine_status.value if evidence.engine_status else "OK"
        }

    @staticmethod
    def procurement_to_dict(procurement: ProcurementSummary) -> Dict[str, Any]:
        """Convert ProcurementSummary to dict."""
        return {
            "packages": procurement.packages,
            "vendors": procurement.vendors,
            "instansi_count": procurement.instansi_count,
            "avg_value": procurement.avg_value,
            "total_value": procurement.total_value,
            "completed": procurement.completed,
            "engine": procurement.engine.value if hasattr(procurement.engine, "value") else str(procurement.engine),
            "engine_status": procurement.engine_status.value if procurement.engine_status else "OK"
        }

    @staticmethod
    def recovery_to_dict(recovery: RecoverySummary) -> Dict[str, Any]:
        """Convert RecoverySummary to dict."""
        return {
            "status": recovery.status,
            "actions": recovery.actions or [],
            "engine": recovery.engine.value if hasattr(recovery.engine, "value") else str(recovery.engine),
            "engine_status": recovery.engine_status.value if recovery.engine_status else "OK"
        }

    @staticmethod
    def dashboard_to_dict(summary: DashboardSummary) -> Dict[str, Any]:
        """Convert DashboardSummary to dict."""
        return {
            "case_id": summary.case_id,
            "fraud": SummaryPresenter.fraud_to_dict(summary.fraud),
            "graph": SummaryPresenter.graph_to_dict(summary.graph),
            "risk": SummaryPresenter.risk_to_dict(summary.risk),
            "evidence": SummaryPresenter.evidence_to_dict(summary.evidence),
            "procurement": SummaryPresenter.procurement_to_dict(summary.procurement),
            "recovery": SummaryPresenter.recovery_to_dict(summary.recovery),
            "confidence": summary.confidence,
            "status": summary.status,
            "generated_at": summary.generated_at.isoformat() if summary.generated_at else None
        }