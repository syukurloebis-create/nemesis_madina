"""
Risk Projection Mapper — Map RiskResult to Projection Data.

Canonical contract v3:
- RiskResult.components: findings_risk, graph_risk, fraud_risk, evidence_risk
- Persistence: canonical columns + legacy (deprecated)

NOTE: File ini tidak dipakai di production path saat ini
(RiskApplicationService adalah dead code), tapi di-patch untuk
mencegah landmine jika service diaktifkan di masa depan.
"""

from typing import Dict, Any
from datetime import datetime, timezone

from backend.intelligence.service import RiskResult
from backend.dtos.risk_snapshot_projection import RiskSnapshotProjection


class RiskProjectionMapper:
    """Map RiskResult to projection data."""

    @staticmethod
    def to_projection_data(result: RiskResult) -> Dict[str, Any]:
        """
        Convert RiskResult to projection data (for risk_scores).

        Canonical mapping v3:
        - findings_risk → findings_risk (canonical) + anomaly_score (legacy)
        - graph_risk    → graph_risk (canonical) + collusion_score (legacy)
        - fraud_risk    → fraud_risk (canonical) + financial_score (legacy)
        - evidence_risk → evidence_risk (canonical)
        """
        components = result.components or {}

        findings_risk = components.get("findings_risk", 0)
        graph_risk = components.get("graph_risk", 0)
        fraud_risk = components.get("fraud_risk", 0)
        evidence_risk = components.get("evidence_risk", 0)

        return {
            "overall_score": result.score,
            "risk_level": result.level,

            # Canonical components (v3)
            "findings_risk": findings_risk,
            "graph_risk": graph_risk,
            "fraud_risk": fraud_risk,
            "evidence_risk": evidence_risk,
            "components": components,
            "weights": result.weights or {},

            # Legacy columns (deprecated, kept for backward compat)
            "anomaly_score": findings_risk,
            "collusion_score": graph_risk,
            "financial_score": fraud_risk,
            "temporal_score": 0,

            # Metadata
            "factors": result.factors or [],
            "recommendations": result.recommendations or [],
        }

    @staticmethod
    def to_case_snapshot(result: RiskResult) -> RiskSnapshotProjection:
        """Convert RiskResult to Case snapshot DTO."""
        return RiskSnapshotProjection(
            score=result.score,
            level=result.level,
            components=result.components,
            calculated_at=datetime.now(timezone.utc).isoformat(),
        )