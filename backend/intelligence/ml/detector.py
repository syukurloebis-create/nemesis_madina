import numpy as np
from typing import List


class AnomalyDetector:
    def __init__(self, threshold: float = 3.0):
        self.threshold = threshold
    
    def detect(self, data: List[float]) -> List[int]:
        if not data:
            return []
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return []
        return [i for i, v in enumerate(data) if abs(v - mean) / std > self.threshold]
    
    def score(self, value: float, historical: List[float]) -> float:
        if not historical:
            return 0.0
        mean = np.mean(historical)
        std = np.std(historical)
        if std == 0:
            return 0.0
        z_score = abs(value - mean) / std
        return min(z_score / 5, 1.0)
