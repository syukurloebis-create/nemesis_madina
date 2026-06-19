"""
Feature Importance - Feature Attribution
"""

from typing import Dict, List, Any, Optional
import numpy as np


class FeatureImportance:
    """Compute feature importance"""
    
    def __init__(self):
        self.feature_history: Dict[str, List[float]] = {}
    
    def add_importance(self, feature_name: str, importance_value: float):
        """Record feature importance"""
        if feature_name not in self.feature_history:
            self.feature_history[feature_name] = []
        self.feature_history[feature_name].append(importance_value)
    
    def get_average_importance(self, feature_name: str) -> float:
        """Get average importance for feature"""
        if feature_name in self.feature_history:
            return float(np.mean(self.feature_history[feature_name]))
        return 0.0
    
    def get_top_features(self, n: int = 10) -> List[tuple]:
        """Get top N features by average importance"""
        averages = [
            (name, self.get_average_importance(name))
            for name in self.feature_history
        ]
        averages.sort(key=lambda x: x[1], reverse=True)
        return averages[:n]
    
    def get_feature_ranking(self) -> Dict[str, int]:
        """Get ranking of features"""
        averages = [
            (name, self.get_average_importance(name))
            for name in self.feature_history
        ]
        averages.sort(key=lambda x: x[1], reverse=True)
        
        return {name: rank for rank, (name, _) in enumerate(averages, 1)}
    
    def get_stability_score(self, feature_name: str) -> float:
        """Get stability of feature importance over time"""
        if feature_name not in self.feature_history:
            return 0.0
        
        values = self.feature_history[feature_name]
        if len(values) < 2:
            return 1.0
        
        # Low variance = high stability
        variance = np.var(values)
        return 1.0 / (1.0 + variance)
