from typing import List, Tuple


class ConfidenceCalibrator:
    def __init__(self):
        self.data: List[Tuple[float, bool]] = []
    
    def add_point(self, predicted: float, actual: bool):
        self.data.append((predicted, actual))
    
    def calibrate(self, raw_score: float) -> float:
        if len(self.data) < 10:
            return raw_score
        pred_mean = sum(p for p, _ in self.data) / len(self.data)
        actual_mean = sum(1 for _, a in self.data if a) / len(self.data)
        factor = actual_mean / pred_mean if pred_mean > 0 else 1.0
        return min(max(raw_score * factor, 0.0), 1.0)
    
    def get_brier_score(self) -> float:
        if not self.data:
            return 1.0
        return sum((p - (1 if a else 0)) ** 2 for p, a in self.data) / len(self.data)
