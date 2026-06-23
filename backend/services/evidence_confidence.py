# services/evidence_confidence.py - Evidence Confidence Engine
import logging
from typing import Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class ConfidenceLevel:
    """Standard confidence levels"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"

class EvidenceConfidence:
    """Evidence confidence calculator"""
    
    @staticmethod
    def calculate(trust_score: float, status: str = "pending") -> str:
        """
        Calculate confidence level based on trust score
        
        Args:
            trust_score: Trust score (0-100)
            status: Evidence status (pending/verified/rejected)
            
        Returns:
            Confidence level: HIGH/MEDIUM/LOW/VERY_LOW
        """
        # Rejected evidence always VERY_LOW
        if status == "rejected":
            return ConfidenceLevel.VERY_LOW
        
        # ============ DETERMINISTIC MAPPING ============
        if trust_score >= 90:
            return ConfidenceLevel.HIGH
        elif trust_score >= 75:
            return ConfidenceLevel.MEDIUM
        elif trust_score >= 50:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    @staticmethod
    def get_confidence_description(level: str) -> str:
        """Get description for confidence level"""
        descriptions = {
            ConfidenceLevel.HIGH: "High confidence - evidence is reliable",
            ConfidenceLevel.MEDIUM: "Medium confidence - evidence needs review",
            ConfidenceLevel.LOW: "Low confidence - evidence requires verification",
            ConfidenceLevel.VERY_LOW: "Very low confidence - evidence likely invalid"
        }
        return descriptions.get(level, "Unknown confidence level")
    
    @staticmethod
    def get_confidence_color(level: str) -> str:
        """Get color for confidence level (for dashboard)"""
        colors = {
            ConfidenceLevel.HIGH: "#22c55e",  # green
            ConfidenceLevel.MEDIUM: "#eab308",  # yellow
            ConfidenceLevel.LOW: "#f97316",  # orange
            ConfidenceLevel.VERY_LOW: "#ef4444"  # red
        }
        return colors.get(level, "#6b7280")  # gray
