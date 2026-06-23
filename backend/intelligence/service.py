# backend/intelligence/service.py - Intelligence Service (FINAL)
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

class IntelligenceService:
    """Intelligence Service for risk scoring"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def calculate_risk_score(
        case_risk: float = 0,
        graph_risk: float = 0,
        fraud_score: float = 0,
        evidence_trust: float = 0
    ) -> Dict[str, Any]:
        """
        Calculate final risk score - FUSION ENGINE
        
        Formula:
        - Case Risk: 30%
        - Graph Risk: 25%
        - Fraud Score: 30%
        - Evidence Trust: 15%
        """
        # ============ FIX: Weighted average ============
        weights = {
            "case": 0.30,
            "graph": 0.25,
            "fraud": 0.30,
            "evidence": 0.15
        }

        final_score = (
            (case_risk or 0) * weights["case"] +
            (graph_risk or 0) * weights["graph"] +
            (fraud_score or 0) * weights["fraud"] +
            (evidence_trust or 0) * weights["evidence"]
        )

        final_score = min(max(final_score, 0), 100)

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

    async def get_evidence_trust(self, case_id: str) -> float:
        """Get evidence trust score for a case"""
        # ============ FIX: Case insensitive + COALESCE ============
        result = await self.session.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN LOWER(status) = 'verified' THEN 1 END) as verified,
                COALESCE(AVG(trust_score), 0) as avg_trust
            FROM evidence 
            WHERE case_id = :case_id
        """), {"case_id": case_id})
        row = result.fetchone()
        
        total_evidence = row[0] or 0
        verified_evidence = row[1] or 0
        avg_trust = float(row[2]) if row[2] else 0
        
        if total_evidence > 0:
            verification_ratio = verified_evidence / total_evidence
            evidence_trust = (avg_trust * 0.7) + (verification_ratio * 100 * 0.3)
            evidence_trust = min(max(evidence_trust, 0), 100)
            logger.info(f"Case {case_id}: total={total_evidence}, verified={verified_evidence}, avg_trust={avg_trust}, evidence_trust={evidence_trust}")
            return evidence_trust
        else:
            return 0

    async def analyze_case(self, case_id: str, fraud_score: float = 0) -> Dict[str, Any]:
        """Analyze a case using all intelligence sources"""
        # 1. Get case risk
        result = await self.session.execute(
            text("SELECT risk_score FROM cases WHERE id = :case_id"),
            {"case_id": case_id}
        )
        row = result.fetchone()
        case_risk = float(row[0]) if row and row[0] else 0

        # 2. Get graph risk
        from intelligence.graph.risk_analyzer import GraphRiskAnalyzer
        graph_data = await GraphRiskAnalyzer.calculate_graph_risk(case_id, self.session)
        graph_risk = graph_data.get("graph_risk", 0)

        # 3. Get evidence trust
        evidence_trust = await self.get_evidence_trust(case_id)

        # 4. Calculate final
        return self.calculate_risk_score(
            case_risk=case_risk,
            graph_risk=graph_risk,
            fraud_score=fraud_score,
            evidence_trust=evidence_trust
        )

    @staticmethod
    def format_response(case_id: str, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for API"""
        return {
            "case_id": case_id,
            "risk_score": risk_data.get("score", 0),
            "risk_level": risk_data.get("level", "LOW"),
            "components": risk_data.get("components", {}),
            "timestamp": datetime.now().isoformat(),
            "version": "v2.0"
        }
