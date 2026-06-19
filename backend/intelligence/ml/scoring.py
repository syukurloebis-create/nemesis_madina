"""
Risk Scoring - Advanced Risk Scoring with Dynamic Weights
"""

from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime


class RiskScorer:
    """Advanced risk scoring with dynamic weights"""
    
    def __init__(self):
        self.weights = {
            "anomaly_score": 0.30,
            "collusion_risk": 0.25,
            "historical_risk": 0.20,
            "velocity": 0.15,
            "volume": 0.10
        }
        self.dynamic_weights_enabled = False
        self.performance_history: List[Dict[str, Any]] = []
    
    def compute_score(self, features: Dict[str, float]) -> float:
        """Compute weighted risk score"""
        score = 0.0
        total_weight = 0.0
        
        for feature, weight in self.weights.items():
            if feature in features:
                score += features[feature] * weight
                total_weight += weight
        
        if total_weight > 0:
            score /= total_weight
        
        return min(max(score, 0.0), 1.0)
    
    def compute_dynamic_score(self, features: Dict[str, float], context: Dict[str, Any] = None) -> float:
        """Compute score with dynamic weights based on context"""
        weights = self.weights.copy()
        
        if context and self.dynamic_weights_enabled:
            # Adjust weights based on context
            if context.get('time_of_day') in ['night', 'weekend']:
                weights['anomaly_score'] *= 1.2
            
            if context.get('entity_type') == 'high_risk':
                weights['historical_risk'] *= 1.3
        
        # Normalize weights
        total = sum(weights.values())
        normalized_weights = {k: v/total for k, v in weights.items()}
        
        score = 0.0
        for feature, weight in normalized_weights.items():
            if feature in features:
                score += features[feature] * weight
        
        return min(max(score, 0.0), 1.0)
    
    def get_severity(self, score: float) -> str:
        """Get severity level from score"""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "info"
    
    def get_recommendation(self, score: float, features: Dict[str, float]) -> str:
        """Get action recommendation based on score and features"""
        if score >= 0.8:
            return "Immediate investigation and containment required"
        elif score >= 0.6:
            return "Escalate to security team for review"
        elif score >= 0.4:
            return "Monitor closely and collect additional evidence"
        elif score >= 0.2:
            return "Log for reference, no immediate action"
        else:
            return "No action needed"
    
    def update_weights(self, new_weights: Dict[str, float]):
        """Update scoring weights"""
        self.weights.update(new_weights)
        # Normalize
        total = sum(self.weights.values())
        for k in self.weights:
            self.weights[k] /= total
    
    def enable_dynamic_weights(self, enabled: bool = True):
        """Enable/disable dynamic weight adjustment"""
        self.dynamic_weights_enabled = enabled
    
    def record_performance(self, predicted_score: float, actual_outcome: bool):
        """Record prediction performance for weight optimization"""
        self.performance_history.append({
            "predicted": predicted_score,
            "actual": actual_outcome,
            "timestamp": datetime.now()
        })
        
        # Keep only last 1000
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
    
    def optimize_weights(self) -> Dict[str, float]:
        """Optimize weights based on historical performance"""
        if len(self.performance_history) < 100:
            return self.weights
        
        # Simple optimization: adjust weights based on feature importance
        # This is a placeholder for more sophisticated optimization
        optimized = self.weights.copy()
        
        # Example: increase weight of features that correlate with actual outcomes
        # Implementation would require feature values storage
        
        return optimized
    
    def get_weights_info(self) -> Dict[str, Any]:
        """Get information about current weights"""
        return {
            "weights": self.weights,
            "dynamic_enabled": self.dynamic_weights_enabled,
            "performance_records": len(self.performance_history)
        }
