from typing import Dict, List, Tuple
import numpy as np


class FeatureImportance:
    def __init__(self):
        self.history: Dict[str, List[float]] = {}
    
    def add(self, feature: str, importance: float):
        if feature not in self.history:
            self.history[feature] = []
        self.history[feature].append(importance)
    
    def get_average(self, feature: str) -> float:
        if feature not in self.history or not self.history[feature]:
            return 0.0
        return float(np.mean(self.history[feature]))
    
    def get_top(self, n: int = 10) -> List[Tuple[str, float]]:
        averages = [(f, self.get_average(f)) for f in self.history]
        averages.sort(key=lambda x: x[1], reverse=True)
        return averages[:n]
