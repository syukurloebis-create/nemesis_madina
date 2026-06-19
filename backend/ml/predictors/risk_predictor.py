# backend/ml/predictors/risk_predictor.py
import numpy as np
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncpg
import sqlite3
import os


class RiskPredictor:
    """AI-powered risk prediction engine."""
    
    def __init__(self, pg_pool: asyncpg.Pool = None):
        self.pg_pool = pg_pool
        self.db_path = os.getenv("SQLITE_PATH", "./nemesis.db")
    
    async def predict_entity_risk(
        self, 
        entity_id: str, 
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """Predict future risk score for an entity."""
        features = await self._extract_features(entity_id)
        
        if not features:
            return {
                "entity_id": entity_id,
                "error": "Insufficient data for prediction",
                "risk_score": 0.5,
                "confidence": 0.3,
            }
        
        historical_scores = features.get("trust_history", [])
        if len(historical_scores) < 5:
            return {
                "entity_id": entity_id,
                "risk_score": features.get("current_risk", 0.5),
                "confidence": 0.4,
                "trend": "stable",
                "message": "Limited historical data",
            }
        
        recent = historical_scores[-7:] if len(historical_scores) >= 7 else historical_scores
        trend = (recent[-1] - recent[0]) / len(recent) if len(recent) > 1 else 0
        
        volatility = np.std(historical_scores[-14:]) if len(historical_scores) >= 14 else 0.05
        predicted_risk = min(1.0, max(0.0, recent[-1] + trend * (days_ahead / 30) + volatility * 0.5))
        
        confidence = min(0.9, 0.5 + len(historical_scores) / 100)
        trend_direction = "increasing" if trend > 0.02 else "decreasing" if trend < -0.02 else "stable"
        
        risk_factors = []
        if features.get("anomaly_count", 0) > 3:
            risk_factors.append("Multiple anomalies detected")
        if features.get("trust_volatility", 0) > 0.1:
            risk_factors.append("High trust volatility")
        
        return {
            "entity_id": entity_id,
            "current_risk": features.get("current_risk", 0.5),
            "predicted_risk": predicted_risk,
            "prediction_days": days_ahead,
            "confidence": confidence,
            "trend": trend_direction,
            "trend_strength": abs(trend),
            "volatility": volatility,
            "risk_factors": risk_factors,
            "predicted_at": datetime.utcnow().isoformat(),
        }
    
    async def predict_anomaly_probability(
        self, 
        entity_id: str
    ) -> Dict[str, Any]:
        """Predict probability of anomaly in next 7 days."""
        features = await self._extract_features(entity_id)
        
        if not features:
            return {
                "entity_id": entity_id,
                "anomaly_probability": 0.1,
                "confidence": 0.3,
            }
        
        base_probability = 0.1
        multiplier = 1.0
        
        if features.get("anomaly_count_30d", 0) > 0:
            multiplier += features.get("anomaly_count_30d", 0) * 0.15
        if features.get("trust_volatility", 0) > 0.1:
            multiplier += features.get("trust_volatility", 0)
        
        probability = min(0.95, base_probability * multiplier)
        confidence = min(0.85, 0.5 + features.get("data_quality", 0.3))
        
        return {
            "entity_id": entity_id,
            "anomaly_probability": probability,
            "confidence": confidence,
            "risk_level": "high" if probability > 0.6 else "medium" if probability > 0.3 else "low",
            "prediction_window_days": 7,
            "predicted_at": datetime.utcnow().isoformat(),
        }
    
    async def _extract_features(self, entity_id: str) -> Dict[str, Any]:
        """Extract features for ML prediction."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if entities table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entities'")
        if not cursor.fetchone():
            conn.close()
            return {}
        
        cursor.execute(
            "SELECT trust_score FROM entities WHERE entity_id = ?",
            (entity_id,)
        )
        entity = cursor.fetchone()
        
        if not entity:
            conn.close()
            return {}
        
        # Get trust history
        cursor.execute(
            "SELECT new_score FROM trust_audit_log WHERE entity_id = ? ORDER BY timestamp ASC",
            (entity_id,)
        )
        trust_history = [row["new_score"] for row in cursor.fetchall()]
        
        # Get anomaly count
        try:
            cursor.execute(
                """
                SELECT COUNT(*) as count 
                FROM anomalies 
                WHERE entity_id = ? AND detected_at > strftime('%s', 'now', '-30 days')
                """,
                (entity_id,)
            )
            anomaly_count = cursor.fetchone()["count"] or 0
        except sqlite3.OperationalError:
            anomaly_count = 0
        
        # Calculate trust volatility
        volatility = np.std(trust_history[-14:]) if len(trust_history) >= 14 else 0
        
        # Get endorsement count (relationships table might not exist)
        endorsement_velocity = 0
        try:
            cursor.execute(
                """
                SELECT COUNT(*) as count 
                FROM relationships 
                WHERE target_id = ?
                """,
                (entity_id,)
            )
            endorsement_velocity = cursor.fetchone()["count"] or 0
        except sqlite3.OperationalError:
            pass
        
        conn.close()
        
        return {
            "current_risk": 1 - (entity["trust_score"] or 0.5),
            "trust_history": trust_history,
            "anomaly_count_30d": anomaly_count,
            "trust_volatility": volatility,
            "endorsement_velocity": endorsement_velocity,
            "cycle_count": 0,
            "data_quality": min(1.0, len(trust_history) / 50),
        }
    
    async def get_high_risk_entities(
        self, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get entities with highest predicted risk."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT entity_id, trust_score
                FROM entities
                ORDER BY trust_score ASC
                LIMIT ?
                """,
                (limit * 2,)
            )
            entities = cursor.fetchall()
        except sqlite3.OperationalError:
            entities = []
        finally:
            conn.close()
        
        predictions = []
        for entity in entities:
            risk_pred = await self.predict_entity_risk(entity[0])
            predictions.append({
                "entity_id": entity[0],
                "current_trust": entity[1],
                "predicted_risk": risk_pred.get("predicted_risk", 0.5),
                "trend": risk_pred.get("trend", "stable"),
                "confidence": risk_pred.get("confidence", 0.5),
            })
        
        predictions.sort(key=lambda x: x["predicted_risk"], reverse=True)
        return predictions[:limit]
