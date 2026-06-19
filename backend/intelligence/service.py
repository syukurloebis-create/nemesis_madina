# backend/intelligence/service.py - Intelligence Service (FIXED)
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class IntelligenceService:
    """Intelligence service for risk calculation"""
    
    @staticmethod
    def calculate_risk_score(
        case_risk: float,
        graph_risk: float,
        fraud_score: float,
        evidence_trust: float
    ) -> Dict[str, Any]:
        """
        Calculate intelligence risk score with components
        
        Args:
            case_risk: Risk from case data (0-100)
            graph_risk: Risk from graph analysis (0-100)
            fraud_score: Risk from ML fraud detection (0-100)
            evidence_trust: Risk from evidence trust (0-100)
            
        Returns:
            Dict with risk_score, risk_level, and components
        """
        # ============ FIX: Weighted average dengan bobot ============
        weights = {
            'case': 0.35,      # 35% dari case risk
            'graph': 0.30,     # 30% dari graph risk
            'fraud': 0.25,     # 25% dari fraud score
            'evidence': 0.10   # 10% dari evidence trust
        }
        
        # Hitung final score
        final_score = (
            (case_risk or 0) * weights['case'] +
            (graph_risk or 0) * weights['graph'] +
            (fraud_score or 0) * weights['fraud'] +
            (evidence_trust or 0) * weights['evidence']
        )
        
        # Normalize ke 0-100
        final_score = min(max(final_score, 0), 100)
        
        # Determine level
        if final_score >= 60:
            level = "HIGH"
        elif final_score >= 30:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        # ============ RETURN WITH COMPONENTS ============
        return {
            "risk_score": round(final_score, 1),
            "risk_level": level,
            "components": {
                "case_risk": round(case_risk or 0, 1),
                "graph_risk": round(graph_risk or 0, 1),
                "fraud_score": round(fraud_score or 0, 1),
                "evidence_trust": round(evidence_trust or 0, 1)
            }
        }
    
    @staticmethod
    def format_response(case_id: str, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format response sesuai standar"""
        return {
            "case_id": case_id,
            "risk_score": risk_data.get("risk_score", 0),
            "risk_level": risk_data.get("risk_level", "LOW"),
            "components": risk_data.get("components", {
                "case_risk": 0,
                "graph_risk": 0,
                "fraud_score": 0,
                "evidence_trust": 0
            }),
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
