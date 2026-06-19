"""
Alert Engine - Rule-based and ML-based alert generation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from enum import Enum

from backend.alerts.websocket_manager import ws_manager
from backend.ml.anomaly_detector import ml_detector

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertEngine:
    """
    Generate real-time alerts based on:
    - ML anomaly detection
    - Rule-based thresholds
    - Collusion detection results
    """
    
    def __init__(self):
        self.alert_history: List[Dict] = []
        self.thresholds = {
            "collusion_risk_critical": 80,
            "collusion_risk_high": 60,
            "anomaly_score_critical": 90,
            "anomaly_score_high": 70,
            "transaction_amount_critical": 10_000_000_000,  # 10B
            "transaction_amount_high": 1_000_000_000,      # 1B
            "velocity_critical": 100,  # transactions per hour
            "velocity_high": 50,
        }
    
    async def check_collusion_alert(self, case_id: str, risk_score: float, triangles: int):
        """Generate alert based on collusion detection results"""
        if risk_score >= self.thresholds["collusion_risk_critical"] and triangles > 0:
            await ws_manager.send_alert({
                "severity": AlertSeverity.CRITICAL,
                "title": f"⚠️ CRITICAL: Collusion Detected (Risk: {risk_score}%)",
                "description": f"Financial triangle pattern detected with {risk_score}% confidence. Immediate investigation required.",
                "case_id": case_id,
                "risk_score": risk_score,
                "triangles_found": triangles,
            }, case_id)
        
        elif risk_score >= self.thresholds["collusion_risk_high"] and triangles > 0:
            await ws_manager.send_alert({
                "severity": AlertSeverity.HIGH,
                "title": f"High Risk Collusion Detected (Risk: {risk_score}%)",
                "description": f"Suspicious circular transaction pattern identified. Priority review recommended.",
                "case_id": case_id,
                "risk_score": risk_score,
                "triangles_found": triangles,
            }, case_id)
    
    async def check_anomaly_alert(self, case_id: str, transactions: List[Dict]):
        """Generate alert based on ML anomaly detection"""
        if not ml_detector.is_trained:
            # Need more data for training
            return
        
        predictions = ml_detector.predict(transactions)
        
        for pred in predictions:
            if pred["anomaly"] and pred["score"] >= self.thresholds["anomaly_score_critical"]:
                await ws_manager.send_alert({
                    "severity": AlertSeverity.CRITICAL,
                    "title": "🚨 CRITICAL: Anomalous Transaction Detected",
                    "description": f"ML model detected anomalous transaction with {pred['score']}% confidence.",
                    "case_id": case_id,
                    "anomaly_score": pred["score"],
                    "transaction_index": pred["index"],
                }, case_id)
            
            elif pred["anomaly"] and pred["score"] >= self.thresholds["anomaly_score_high"]:
                await ws_manager.send_alert({
                    "severity": AlertSeverity.HIGH,
                    "title": "Suspicious Transaction Detected",
                    "description": f"ML model flagged unusual transaction pattern ({pred['score']}% confidence).",
                    "case_id": case_id,
                    "anomaly_score": pred["score"],
                }, case_id)
    
    async def check_threshold_alert(self, case_id: str, amount: float, velocity: int):
        """Generate alert based on static thresholds"""
        if amount >= self.thresholds["transaction_amount_critical"]:
            await ws_manager.send_alert({
                "severity": AlertSeverity.CRITICAL,
                "title": "💰 CRITICAL: Massive Transaction Detected",
                "description": f"Transaction amount Rp {amount:,.0f} exceeds critical threshold.",
                "case_id": case_id,
                "amount": amount,
            }, case_id)
        
        elif amount >= self.thresholds["transaction_amount_high"]:
            await ws_manager.send_alert({
                "severity": AlertSeverity.HIGH,
                "title": "Large Transaction Alert",
                "description": f"Transaction amount Rp {amount:,.0f} exceeds high threshold.",
                "case_id": case_id,
                "amount": amount,
            }, case_id)
        
        if velocity >= self.thresholds["velocity_critical"]:
            await ws_manager.send_alert({
                "severity": AlertSeverity.CRITICAL,
                "title": "⚡ CRITICAL: Unusual Transaction Velocity",
                "description": f"Transaction velocity ({velocity} tx/hour) exceeds critical threshold.",
                "case_id": case_id,
                "velocity": velocity,
            }, case_id)


alert_engine = AlertEngine()