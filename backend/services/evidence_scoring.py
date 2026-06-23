# services/evidence_scoring.py - Evidence Confidence Engine (FIXED)
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfidenceLevel:
    """Standard confidence levels"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"

class EvidenceScorer:
    """Evidence scoring and confidence calculation"""
    
    # ============================================
    # FIX: Deterministic Confidence Mapping
    # ============================================
    @staticmethod
    def calculate_confidence(trust_score: float, status: str = "pending") -> str:
        """
        Calculate confidence level based on trust score ONLY.
        
        Args:
            trust_score: Trust score (0-100)
            status: Evidence status (pending/verified/rejected)
            
        Returns:
            Confidence level: HIGH/MEDIUM/LOW/VERY_LOW
        """
        # Rejected evidence always VERY_LOW
        if status == "rejected":
            return ConfidenceLevel.VERY_LOW
        
        # ============ FIX: Deterministic mapping ============
        if trust_score >= 90:
            return ConfidenceLevel.HIGH
        elif trust_score >= 75:
            return ConfidenceLevel.MEDIUM
        elif trust_score >= 50:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    @staticmethod
    def calculate_trust_score(
        file_hash: str,
        file_size: int,
        file_type: str,
        verified: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate initial trust score for evidence
        
        Returns:
            Trust score (0-100)
        """
        base_score = 50.0
        
        # Hash quality
        if file_hash and len(file_hash) == 64:
            base_score += 20
        
        # File size (not empty)
        if file_size > 0:
            base_score += 10
        
        # File type
        trusted_types = ["application/pdf", "image/png", "image/jpeg", 
                        "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        if file_type in trusted_types:
            base_score += 10
        
        # Verified
        if verified:
            base_score += 10
        
        return min(base_score, 100)
    
    @staticmethod
    def get_evidence_quality(
        trust_score: float,
        status: str,
        verified_count: int = 0,
        total_evidence: int = 1,
        immutable_count: int = 0
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive evidence quality score
        
        Args:
            trust_score: Average trust score (0-100)
            status: Evidence status
            verified_count: Number of verified evidence
            total_evidence: Total evidence
            immutable_count: Number of immutable evidence
            
        Returns:
            Quality metrics
        """
        # Verification ratio
        verification_ratio = verified_count / total_evidence if total_evidence > 0 else 0
        
        # Immutable ratio
        immutable_ratio = immutable_count / total_evidence if total_evidence > 0 else 0
        
        # ============ NEW FORMULA ============
        # Evidence Quality Index (EQI)
        # 40% Integrity + 30% Trust + 20% Verification + 10% Freshness
        integrity_score = immutable_ratio * 100
        trust_component = trust_score * 0.3
        verification_component = verification_ratio * 100 * 0.2
        freshness_component = 80  # Default, bisa dihitung dari timestamp
        
        quality_score = (
            (integrity_score * 0.4) +
            (trust_score * 0.3) +
            (verification_ratio * 100 * 0.2) +
            (freshness_component * 0.1)
        )
        
        return {
            "quality_score": round(min(quality_score, 100), 1),
            "verification_ratio": round(verification_ratio * 100, 1),
            "integrity_score": round(integrity_score, 1),
            "trust_component": round(trust_component, 1),
            "verification_component": round(verification_component, 1),
            "risk_level": "HIGH" if quality_score > 70 else "MEDIUM" if quality_score > 50 else "LOW"
        }
