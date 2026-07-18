"""ML Anomaly Detector - Procurement fraud detection"""

import uuid
import math
from typing import Dict, Any, List, Optional
from datetime import datetime


class AnomalyDetector:
    """Rule-based anomaly detection for procurement fraud"""
    
    @staticmethod
    def detect_anomaly(procurement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in procurement data - STATIC METHOD"""
        
        contract_value = procurement_data.get("contract_value", 0)
        market_average = procurement_data.get("market_average", contract_value)
        vendor_history = procurement_data.get("vendor_history", "unknown")
        procurement_method = procurement_data.get("procurement_method", "unknown")
        
        # Calculate price markup
        if market_average > 0:
            price_markup = (contract_value - market_average) / market_average
        else:
            price_markup = 0
        
        # Vendor risk score
        vendor_risk_map = {
            "low": 0.1,
            "medium": 0.4,
            "high": 0.7,
            "critical": 0.9,
            "unknown": 0.3
        }
        vendor_risk_score = vendor_risk_map.get(vendor_history, 0.3)
        
        # Method risk score
        method_risk_map = {
            "tender": 0.1,
            "limited_tender": 0.3,
            "direct": 0.7,
            "emergency": 0.5,
            "unknown": 0.4
        }
        method_risk_score = method_risk_map.get(procurement_method, 0.4)
        
        # Calculate anomaly score
        anomaly_score = (
            (min(max(price_markup, 0), 1) * 0.5) +
            (vendor_risk_score * 0.3) +
            (method_risk_score * 0.2)
        )
        
        # Determine risk level
        if anomaly_score >= 0.7:
            risk_level = "critical"
        elif anomaly_score >= 0.5:
            risk_level = "high"
        elif anomaly_score >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Generate findings
        findings = []
        if price_markup > 0.3:
            findings.append(f"Harga {price_markup*100:.0f}% di atas pasar")
        if vendor_history in ["high", "critical"]:
            findings.append(f"Vendor berisiko {vendor_history}")
        if procurement_method == "direct":
            findings.append("Penunjukan langsung tanpa tender")
        
        if not findings:
            findings.append("Parameter dalam batas normal, namun perlu monitoring")
        
        return {
            "anomaly_id": str(uuid.uuid4()),
            "score": round(anomaly_score, 3),
            "risk_level": risk_level,
            "findings": findings,
            "details": {
                "price_markup": round(price_markup, 3),
                "vendor_risk_score": vendor_risk_score,
                "method_risk_score": method_risk_score,
                "contract_value": contract_value,
                "market_average": market_average
            },
            "recommendation": AnomalyDetector._get_recommendation(risk_level, findings)
        }
    
    @staticmethod
    def get_confidence_score(anomaly_score: float) -> float:
        """Calculate confidence score for detection"""
        confidence = 0.5 + (abs(anomaly_score - 0.5) * 0.8)
        return min(0.99, max(0.5, confidence))
    
    @staticmethod
    def _get_recommendation(risk_level: str, findings: List[str]) -> str:
        """Generate recommendation based on risk level"""
        if risk_level == "critical":
            return "Segera lakukan audit khusus dan laporkan ke APIP/BPK"
        elif risk_level == "high":
            return "Perlu verifikasi lebih lanjut oleh tim audit"
        elif risk_level == "medium":
            return "Monitoring berkelanjutan dan dokumentasi tambahan"
        else:
            return "Dalam batas normal, lanjutkan monitoring rutin"


    @staticmethod
    def detect_anomaly_calibrated(procurement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies with calibrated risk scoring"""
        result = AnomalyDetector.detect_anomaly(procurement_data)
        
        from ml.calibration import calibrator
        calibrated = calibrator.calibrate(result["score"], result.get("confidence", 0.5))
        
        result["calibrated_score"] = calibrated.calibrated_score
        result["calibrated_risk_level"] = calibrated.risk_level
        result["calibration_info"] = {
            "raw_score": calibrated.raw_score,
            "calibrated_score": calibrated.calibrated_score,
            "threshold_used": calibrated.threshold_used
        }
        
        # Override with calibrated values if more accurate
        if calibrated.risk_level != result["risk_level"]:
            result["risk_level"] = calibrated.risk_level
            result["score"] = calibrated.calibrated_score
        
        return result

# Singleton instance for backward compatibility
detector = AnomalyDetector()


