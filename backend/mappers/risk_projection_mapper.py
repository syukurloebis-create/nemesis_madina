"""
Risk Projection Mapper — Map RiskResult to Projection Data.
"""

from typing import Dict, Any
from datetime import datetime, timezone

from backend.intelligence.service import RiskResult  
from backend.dtos.risk_snapshot_projection import RiskSnapshotProjection


class RiskProjectionMapper:
    """Map RiskResult to projection data."""

    @staticmethod
    def to_projection_data(result: RiskResult) -> Dict[str, Any]:
        """Convert RiskResult to projection data (for risk_scores)."""
        return {
            "overall_score": result.score,
            "risk_level": result.level,
            "anomaly_score": result.components.get("case_risk", 0),
            "collusion_score": result.components.get("graph_risk", 0),
            "financial_score": result.components.get("fraud_score", 0),
            "temporal_score": 0,
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