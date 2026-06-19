"""Risk Score Calibration - Production-grade threshold mapping"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class CalibratedRisk:
    raw_score: float
    calibrated_score: float
    risk_level: str
    confidence: float
    threshold_used: str

class RiskCalibrator:
    """Calibrate risk scores to proper thresholds"""
    
    # Production thresholds based on historical audit data
    THRESHOLDS = {
        "critical": 0.75,
        "high": 0.60,
        "medium": 0.40,
        "low": 0.20
    }
    
    @classmethod
    def calibrate(cls, raw_score: float, confidence: float) -> CalibratedRisk:
        """Calibrate raw score to proper risk level"""
        
        # Apply confidence penalty for low confidence detections
        if confidence < 0.6:
            confidence_penalty = 0.1 * (0.6 - confidence)
            calibrated = max(0, raw_score - confidence_penalty)
        else:
            calibrated = raw_score
        
        # Determine risk level based on calibrated score
        if calibrated >= cls.THRESHOLDS["critical"]:
            risk_level = "critical"
        elif calibrated >= cls.THRESHOLDS["high"]:
            risk_level = "high"
        elif calibrated >= cls.THRESHOLDS["medium"]:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return CalibratedRisk(
            raw_score=round(raw_score, 3),
            calibrated_score=round(calibrated, 3),
            risk_level=risk_level,
            confidence=round(confidence, 3),
            threshold_used="production_v1"
        )
    
    @classmethod
    def get_threshold_metadata(cls) -> Dict:
        """Get threshold configuration for audit trail"""
        return {
            "version": "1.0.0",
            "thresholds": cls.THRESHOLDS,
            "calibration_date": "2024-12-02",
            "methodology": "historical_audit_data_analysis"
        }

calibrator = RiskCalibrator()


class ConfidenceCalibrator:
    """Calibrate ML confidence scores"""
    
    @staticmethod
    def calibrate(raw_score: float, context: dict) -> float:
        """Calibrate based on historical accuracy"""
        # Weight based on data completeness
        completeness_weight = len(context.get("features", [])) / 10
        
        # Historical accuracy adjustment
        historical_bias = 0.05  # From training data
        
        calibrated = min(0.95, raw_score * completeness_weight + historical_bias)
        return round(calibrated, 3)
