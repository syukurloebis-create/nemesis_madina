# services/evidence_intelligence.py - Evidence Intelligence Score
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class EvidenceIntelligence:
    """Evidence Intelligence Score Calculator"""
    
    @staticmethod
    def calculate_eis(
        trust_score: float,
        verification_ratio: float,
        integrity_score: float,
        confidence_level: str,
        status: str
    ) -> Dict[str, Any]:
        """
        Calculate Evidence Intelligence Score (EIS)
        
        Formula:
        - 40% Trust Score
        - 30% Verification Ratio
        - 20% Integrity
        - 10% Confidence Quality
        
        Args:
            trust_score: Average trust score (0-100)
            verification_ratio: Verified / Total (0-1)
            integrity_score: Immutable / Total (0-100)
            confidence_level: HIGH/MEDIUM/LOW/VERY_LOW
            status: pending/verified/rejected
            
        Returns:
            Evidence Intelligence metrics
        """
        # Confidence quality score
        confidence_scores = {
            "HIGH": 100,
            "MEDIUM": 75,
            "LOW": 50,
            "VERY_LOW": 25
        }
        confidence_quality = confidence_scores.get(confidence_level, 50)
        
        # Calculate EIS
        eis = (
            (trust_score * 0.4) +
            (verification_ratio * 100 * 0.3) +
            (integrity_score * 0.2) +
            (confidence_quality * 0.1)
        )
        
        # Determine level
        if eis >= 80:
            level = "EXCELLENT"
        elif eis >= 60:
            level = "GOOD"
        elif eis >= 40:
            level = "MEDIUM"
        else:
            level = "POOR"
        
        return {
            "eis": round(min(eis, 100), 1),
            "level": level,
            "components": {
                "trust_component": round(trust_score * 0.4, 1),
                "verification_component": round(verification_ratio * 100 * 0.3, 1),
                "integrity_component": round(integrity_score * 0.2, 1),
                "confidence_component": round(confidence_quality * 0.1, 1)
            },
            "recommendation": EvidenceIntelligence._get_recommendation(eis, status)
        }
    
    @staticmethod
    def _get_recommendation(eis: float, status: str) -> str:
        """Get recommendation based on EIS"""
        if status == "rejected":
            return "Evidence rejected - review required"
        elif status == "pending":
            return "Evidence pending verification - quality uncertain"
        elif eis >= 80:
            return "Evidence reliable - ready for risk analysis"
        elif eis >= 60:
            return "Evidence moderately reliable - proceed with caution"
        else:
            return "Evidence quality low - seek additional verification"
    
    @staticmethod
    def get_evidence_contribution(eis: float) -> float:
        """
        Get evidence contribution to risk score
        Maps EIS (0-100) to risk contribution (0-100)
        """
        # EIS 0-100 → evidence_trust 0-100
        return min(eis, 100)
