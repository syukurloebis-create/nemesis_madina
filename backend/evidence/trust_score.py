# backend/evidence/trust_score.py
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid
import math


class TrustLevel(str, Enum):
    """Level kepercayaan evidence"""
    VERIFIED = "VERIFIED"       # 90-100% - Terverifikasi penuh
    HIGH = "HIGH"               # 70-89% - Tingkat kepercayaan tinggi
    MEDIUM = "MEDIUM"           # 40-69% - Perlu verifikasi tambahan
    LOW = "LOW"                 # 10-39% - Perlu verifikasi signifikan
    UNVERIFIED = "UNVERIFIED"   # 0-9% - Belum diverifikasi


class TrustScoreFactors:
    """Faktor-faktor yang mempengaruhi trust score"""
    
    # Weights untuk setiap faktor
    WEIGHT_SOURCE = 0.25
    WEIGHT_INTEGRITY = 0.30
    WEIGHT_CUSTODY = 0.20
    WEIGHT_CONSISTENCY = 0.15
    WEIGHT_TIMESTAMP = 0.10
    
    @staticmethod
    def calculate_source_score(source_type: str, source_trust_level: str) -> float:
        """Hitung skor berdasarkan sumber"""
        source_scores = {
            "SYSTEM_GENERATED": 1.0,
            "INTERNAL": 0.9,
            "WHISTLEBLOWER": 0.6,
            "EXTERNAL": 0.5,
            "THIRD_PARTY": 0.4
        }
        return source_scores.get(source_type, 0.5)
    
    @staticmethod
    def calculate_integrity_score(hash_validated: bool, hash_match: bool) -> float:
        """Hitung skor berdasarkan integritas hash"""
        if hash_validated and hash_match:
            return 1.0
        elif hash_validated:
            return 0.5
        else:
            return 0.0
    
    @staticmethod
    def calculate_custody_score(custody_events: List[Dict], current_holder: str) -> float:
        """Hitung skor berdasarkan chain of custody"""
        if not custody_events:
            return 0.3
        
        # Base score
        score = 0.5
        
        # More events = better tracking
        score += min(0.3, len(custody_events) * 0.05)
        
        # Check if chain is continuous
        is_continuous = all(
            custody_events[i]["next_holder"] == custody_events[i+1]["previous_holder"]
            for i in range(len(custody_events) - 1)
        )
        if is_continuous:
            score += 0.2
        
        return min(1.0, score)
    
    @staticmethod
    def calculate_consistency_score(file_metadata: Dict, declared_metadata: Dict) -> float:
        """Hitung skor berdasarkan konsistensi metadata"""
        matches = 0
        total = 0
        
        if "file_size" in file_metadata and "declared_size" in declared_metadata:
            total += 1
            if abs(file_metadata["file_size"] - declared_metadata["declared_size"]) < 1000:
                matches += 1
        
        if "created_date" in file_metadata and "claimed_date" in declared_metadata:
            total += 1
            if file_metadata["created_date"] == declared_metadata["claimed_date"]:
                matches += 1
        
        if total == 0:
            return 0.5
        
        return matches / total
    
    @staticmethod
    def calculate_timestamp_score(uploaded_at: datetime, modified_at: Optional[datetime]) -> float:
        """Hitung skor berdasarkan timestamp"""
        now = datetime.utcnow()
        age_days = (now - uploaded_at).days
        
        if age_days < 7:
            return 1.0
        elif age_days < 30:
            return 0.9
        elif age_days < 90:
            return 0.8
        elif age_days < 365:
            return 0.7
        else:
            return 0.5


class TrustScoreEngine:
    """Engine untuk menghitung trust score evidence"""
    
    def __init__(self):
        self.factors = TrustScoreFactors()
    
    def calculate(
        self,
        evidence_id: uuid.UUID,
        source_type: str,
        source_trust_level: str,
        hash_validated: bool,
        hash_match: bool,
        custody_events: List[Dict],
        current_holder: str,
        file_metadata: Dict,
        declared_metadata: Dict,
        uploaded_at: datetime,
        modified_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive trust score"""
        
        # Calculate individual factor scores
        source_score = self.factors.calculate_source_score(source_type, source_trust_level)
        integrity_score = self.factors.calculate_integrity_score(hash_validated, hash_match)
        custody_score = self.factors.calculate_custody_score(custody_events, current_holder)
        consistency_score = self.factors.calculate_consistency_score(file_metadata, declared_metadata)
        timestamp_score = self.factors.calculate_timestamp_score(uploaded_at, modified_at)
        
        # Calculate weighted total score (0-100)
        total_score = (
            source_score * self.factors.WEIGHT_SOURCE +
            integrity_score * self.factors.WEIGHT_INTEGRITY +
            custody_score * self.factors.WEIGHT_CUSTODY +
            consistency_score * self.factors.WEIGHT_CONSISTENCY +
            timestamp_score * self.factors.WEIGHT_TIMESTAMP
        ) * 100
        
        # Round to 1 decimal
        total_score = round(total_score, 1)
        
        # Determine trust level
        if total_score >= 90:
            trust_level = TrustLevel.VERIFIED
        elif total_score >= 70:
            trust_level = TrustLevel.HIGH
        elif total_score >= 40:
            trust_level = TrustLevel.MEDIUM
        elif total_score >= 10:
            trust_level = TrustLevel.LOW
        else:
            trust_level = TrustLevel.UNVERIFIED
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            source_score, integrity_score, custody_score,
            consistency_score, timestamp_score
        )
        
        return {
            "evidence_id": str(evidence_id),
            "total_score": total_score,
            "trust_level": trust_level.value,
            "factors": {
                "source_score": round(source_score * 100, 1),
                "integrity_score": round(integrity_score * 100, 1),
                "custody_score": round(custody_score * 100, 1),
                "consistency_score": round(consistency_score * 100, 1),
                "timestamp_score": round(timestamp_score * 100, 1)
            },
            "weights": {
                "source": self.factors.WEIGHT_SOURCE,
                "integrity": self.factors.WEIGHT_INTEGRITY,
                "custody": self.factors.WEIGHT_CUSTODY,
                "consistency": self.factors.WEIGHT_CONSISTENCY,
                "timestamp": self.factors.WEIGHT_TIMESTAMP
            },
            "recommendations": recommendations,
            "calculated_at": datetime.utcnow().isoformat()
        }
    
    def _generate_recommendations(
        self,
        source_score: float,
        integrity_score: float,
        custody_score: float,
        consistency_score: float,
        timestamp_score: float
    ) -> List[str]:
        """Generate recommendations for improving trust score"""
        
        recommendations = []
        
        if source_score < 0.6:
            recommendations.append("Verify source of evidence - current source has low trust level")
        
        if integrity_score < 0.7:
            recommendations.append("Validate file hash integrity - hash verification pending or failed")
        
        if custody_score < 0.6:
            recommendations.append("Complete chain of custody documentation - missing transfer records")
        
        if consistency_score < 0.7:
            recommendations.append("Verify metadata consistency - file metadata doesn't match declaration")
        
        if timestamp_score < 0.7:
            recommendations.append("Evidence is older than recommended - consider refreshing verification")
        
        if not recommendations:
            recommendations.append("Evidence trust score is satisfactory - no immediate action required")
        
        return recommendations
    
    def calculate_batch(
        self,
        evidence_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculate trust scores for multiple evidence items"""
        
        results = []
        for evidence in evidence_list:
            result = self.calculate(
                evidence_id=evidence.get("evidence_id"),
                source_type=evidence.get("source_type", "EXTERNAL"),
                source_trust_level=evidence.get("source_trust_level", "MEDIUM"),
                hash_validated=evidence.get("hash_validated", False),
                hash_match=evidence.get("hash_match", False),
                custody_events=evidence.get("custody_events", []),
                current_holder=evidence.get("current_holder", ""),
                file_metadata=evidence.get("file_metadata", {}),
                declared_metadata=evidence.get("declared_metadata", {}),
                uploaded_at=evidence.get("uploaded_at", datetime.utcnow()),
                modified_at=evidence.get("modified_at")
            )
            results.append(result)
        
        return results
    
    def get_case_trust_summary(self, evidence_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get trust summary for a case based on its evidence"""
        
        if not evidence_scores:
            return {
                "total_evidence": 0,
                "average_trust_score": 0,
                "trust_level": TrustLevel.UNVERIFIED.value,
                "verified_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "unverified_count": 0
            }
        
        scores = [e["total_score"] for e in evidence_scores]
        avg_score = sum(scores) / len(scores)
        
        # Count by trust level
        counts = {
            TrustLevel.VERIFIED: 0,
            TrustLevel.HIGH: 0,
            TrustLevel.MEDIUM: 0,
            TrustLevel.LOW: 0,
            TrustLevel.UNVERIFIED: 0
        }
        
        for score in evidence_scores:
            level = score["trust_level"]
            counts[TrustLevel(level)] += 1
        
        # Determine overall trust level
        if avg_score >= 90:
            overall_level = TrustLevel.VERIFIED
        elif avg_score >= 70:
            overall_level = TrustLevel.HIGH
        elif avg_score >= 40:
            overall_level = TrustLevel.MEDIUM
        elif avg_score >= 10:
            overall_level = TrustLevel.LOW
        else:
            overall_level = TrustLevel.UNVERIFIED
        
        return {
            "total_evidence": len(evidence_scores),
            "average_trust_score": round(avg_score, 1),
            "trust_level": overall_level.value,
            "verified_count": counts[TrustLevel.VERIFIED],
            "high_count": counts[TrustLevel.HIGH],
            "medium_count": counts[TrustLevel.MEDIUM],
            "low_count": counts[TrustLevel.LOW],
            "unverified_count": counts[TrustLevel.UNVERIFIED]
        }


# Singleton instance
_trust_score_engine = None

def get_trust_score_engine() -> TrustScoreEngine:
    """Get singleton trust score engine"""
    global _trust_score_engine
    if _trust_score_engine is None:
        _trust_score_engine = TrustScoreEngine()
    return _trust_score_engine