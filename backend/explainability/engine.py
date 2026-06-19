"""Explainability Engine - Human-readable explanations for AI decisions"""

import uuid
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class Explanation:
    id: str
    evidence_id: str
    score: float
    confidence: float
    reasons: List[str]
    feature_importance: Dict[str, float]
    lineage: List[str]
    timestamp: datetime
    hash: str
    
    def compute_hash(self) -> str:
        content = f"{self.id}{self.evidence_id}{self.score}{self.confidence}{self.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()

class ExplainabilityEngine:
    """Generate human-readable explanations for audit findings"""
    
    _explanations: Dict[str, Explanation] = {}
    
    @staticmethod
    def _calculate_feature_importance(features: Dict[str, Any]) -> Dict[str, float]:
        """Calculate feature importance based on rules"""
        importance = {}
        
        # Procurement anomalies
        if "price_markup" in features:
            importance["price_markup"] = min(1.0, features.get("price_markup", 0) * 2)
        
        if "vendor_risk" in features:
            risk_map = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
            importance["vendor_risk"] = risk_map.get(features.get("vendor_risk", "low"), 0.3)
        
        if "procurement_method" in features:
            method_map = {"tender": 0.1, "direct": 0.7, "emergency": 0.5}
            importance["procurement_method"] = method_map.get(features.get("procurement_method"), 0.3)
        
        if "anomaly_score" in features:
            importance["anomaly_score"] = features.get("anomaly_score", 0)
        
        if "historical_issues" in features:
            importance["historical_issues"] = min(1.0, features.get("historical_issues", 0) / 10)
        
        if "collusion_risk" in features:
            importance["collusion_risk"] = features.get("collusion_risk", 0)
        
        return importance
    
    @staticmethod
    def _generate_reasons(features: Dict[str, Any], importance: Dict[str, float]) -> List[str]:
        """Generate human-readable reasons for the finding"""
        reasons = []
        
        # Price markup
        price_markup = features.get("price_markup", 0)
        if price_markup > 0.3:
            reasons.append(f"Harga {price_markup*100:.0f}% lebih tinggi dari rata-rata pasar")
        elif price_markup > 0.15:
            reasons.append(f"Terdapat selisih harga {price_markup*100:.0f}% dari nilai wajar")
        
        # Vendor risk
        vendor_risk = features.get("vendor_risk", "low")
        if vendor_risk in ["high", "critical"]:
            reasons.append(f"Vendor memiliki tingkat risiko {vendor_risk} berdasarkan historis")
        
        # Procurement method
        method = features.get("procurement_method", "")
        if method == "direct":
            reasons.append("Metode penunjukan langsung meningkatkan risiko markup harga")
        elif method == "emergency":
            reasons.append("Pengadaan darurat perlu verifikasi lebih lanjut")
        
        # Anomaly score
        anomaly = features.get("anomaly_score", 0)
        if anomaly > 0.7:
            reasons.append(f"Skor anomali tinggi ({anomaly:.0%}) mengindikasikan potensi irregularitas")
        
        # Historical issues
        historical = features.get("historical_issues", 0)
        if historical > 3:
            reasons.append(f"Terdapat {historical} isu serupa dalam 12 bulan terakhir")
        
        # Collusion risk
        collusion = features.get("collusion_risk", 0)
        if collusion > 0.6:
            reasons.append("Pola hubungan antar vendor mengindikasikan potensi kolusi")
        
        # Default reason if none generated
        if not reasons:
            reasons.append("Parameter yang dianalisis berada dalam batas normal")
        
        return reasons
    
    def explain(
        self,
        evidence_id: str,
        features: Dict[str, Any],
        score: float = None,
        confidence: float = None
    ) -> Dict[str, Any]:
        """Generate explanation for a finding"""
        
        # Calculate importance and reasons
        importance = self._calculate_feature_importance(features)
        reasons = self._generate_reasons(features, importance)
        
        # Use provided score or calculate from importance
        if score is None:
            score = sum(importance.values()) / max(len(importance), 1)
        
        # Calculate confidence based on data completeness
        if confidence is None:
            confidence = min(0.95, 0.5 + (len(importance) / 10))
        
        # Create explanation
        explanation = Explanation(
            id=str(uuid.uuid4()),
            evidence_id=evidence_id,
            score=round(score, 3),
            confidence=round(confidence, 3),
            reasons=reasons,
            feature_importance=importance,
            lineage=[],
            timestamp=datetime.now(),
            hash=""
        )
        explanation.hash = explanation.compute_hash()
        
        # Store
        self._explanations[explanation.id] = explanation
        
        return {
            "id": explanation.id,
            "evidence_id": explanation.evidence_id,
            "score": explanation.score,
            "confidence": explanation.confidence,
            "reasons": explanation.reasons,
            "feature_importance": explanation.feature_importance,
            "timestamp": explanation.timestamp.isoformat(),
            "hash": explanation.hash
        }
    
    def get_explanation(self, explanation_id: str) -> Optional[Dict]:
        """Get stored explanation by ID"""
        exp = self._explanations.get(explanation_id)
        if not exp:
            return None
        
        return {
            "id": exp.id,
            "evidence_id": exp.evidence_id,
            "score": exp.score,
            "confidence": exp.confidence,
            "reasons": exp.reasons,
            "feature_importance": exp.feature_importance,
            "timestamp": exp.timestamp.isoformat(),
            "hash": exp.hash
        }
    
    def get_reasoning_chain(self, evidence_id: str) -> Dict:
        """Get reasoning chain for an evidence"""
        explanations = [
            exp for exp in self._explanations.values()
            if exp.evidence_id == evidence_id
        ]
        
        if not explanations:
            return {"evidence_id": evidence_id, "explanations": [], "chain_length": 0}
        
        # Sort by timestamp
        explanations.sort(key=lambda x: x.timestamp)
        latest = explanations[-1]
        
        return {
            "evidence_id": evidence_id,
            "explanations": [
                {
                    "id": e.id,
                    "reasons": e.reasons,
                    "score": e.score,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in explanations
            ],
            "chain_length": len(explanations),
            "latest_score": latest.score,
            "latest_confidence": latest.confidence,
            "primary_reason": latest.reasons[0] if latest.reasons else "No specific reason"
        }
    
    def calibrate_confidence(self, evidence_id: str, actual_outcome: str) -> Dict:
        """Calibrate confidence based on actual outcomes"""
        # Find explanations for this evidence
        explanations = [
            exp for exp in self._explanations.values()
            if exp.evidence_id == evidence_id
        ]
        
        if not explanations:
            return {"message": "No explanations found for this evidence"}
        
        latest = explanations[-1]
        
        # Simple calibration: adjust confidence based on outcome
        calibration = {
            "true_positive": min(0.99, latest.confidence + 0.05),
            "false_positive": max(0.5, latest.confidence - 0.2),
            "true_negative": min(0.95, latest.confidence + 0.02),
            "false_negative": max(0.3, latest.confidence - 0.3)
        }
        
        return {
            "evidence_id": evidence_id,
            "original_confidence": latest.confidence,
            "calibrated_confidence": calibration.get(actual_outcome, latest.confidence),
            "actual_outcome": actual_outcome,
            "message": "Confidence calibrated based on actual outcome"
        }

# Singleton instance
explainer = ExplainabilityEngine()
