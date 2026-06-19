# intelligence/service.py - Intelligence Service
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class IntelligenceService:
    """Intelligence Service for risk scoring"""

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def calculate_risk_score(
        case_risk: float,
        graph_risk: float = 0,
        fraud_score: float = 0,
        evidence_trust: float = 0
    ) -> Dict[str, Any]:
        """Calculate final risk score"""
        weights = {
            "case": 0.25,
            "graph": 0.25,
            "fraud": 0.30,
            "evidence": 0.20
        }

        final_score = (
            (case_risk or 0) * weights["case"] +
            (graph_risk or 0) * weights["graph"] +
            (fraud_score or 0) * weights["fraud"] +
            (evidence_trust or 0) * weights["evidence"]
        )

        if final_score >= 80:
            level = "CRITICAL"
        elif final_score >= 60:
            level = "HIGH"
        elif final_score >= 40:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "score": round(final_score, 2),
            "level": level,
            "components": {
                "case_risk": case_risk,
                "graph_risk": graph_risk,
                "fraud_score": fraud_score,
                "evidence_trust": evidence_trust
            },
            "weights": weights
        }

    async def analyze_case(self, case_id: str) -> Dict[str, Any]:
        """Analyze a case using all intelligence sources"""
        from sqlalchemy import text
        
        # Get case risk
        result = await self.session.execute(
            text("SELECT risk_score FROM cases WHERE id = :case_id"),
            {"case_id": case_id}
        )
        row = result.fetchone()
        case_risk = float(row[0]) if row and row[0] else 0
        
        # Get graph risk
        from backend.intelligence.graph.risk_analyzer import GraphRiskAnalyzer
        graph_data = await GraphRiskAnalyzer.calculate_graph_risk(case_id, self.session)
        graph_risk = graph_data.get("graph_risk", 0)
        
        # Calculate final
        return self.calculate_risk_score(
            case_risk=case_risk,
            graph_risk=graph_risk,
            fraud_score=0,
            evidence_trust=0
        )

    async def get_case_intelligence_summary(self, case_id: str) -> Dict[str, Any]:
        """Get complete intelligence summary for a case"""
        result = await self.analyze_case(case_id)
        result["case_id"] = case_id
        return result
