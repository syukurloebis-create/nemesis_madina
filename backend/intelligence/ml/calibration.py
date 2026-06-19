"""
Confidence Calibration - Advanced Probability Calibration
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.isotonic import IsotonicRegression
from scipy import special


class ConfidenceCalibrator:
    """Advanced confidence calibration using multiple methods"""
    
    def __init__(self, method: str = 'platt'):
        """
        method: 'platt', 'isotonic', 'beta', or 'none'
        """
        self.method = method
        self.calibration_data: List[Tuple[float, int]] = []  # (predicted, actual)
        self._platt_a = None
        self._platt_b = None
        self._isotonic_model = None
        self._alpha = 1.0  # Beta distribution alpha
        self._beta = 1.0   # Beta distribution beta
    
    def add_calibration_point(self, predicted_score: float, actual_outcome: bool):
        """Add calibration data point"""
        self.calibration_data.append((predicted_score, 1 if actual_outcome else 0))
        
        # Keep only recent data
        if len(self.calibration_data) > 10000:
            self.calibration_data = self.calibration_data[-5000:]
    
    def calibrate(self, raw_score: float) -> float:
        """Calibrate raw confidence score"""
        if len(self.calibration_data) < 50:
            return raw_score
        
        if self.method == 'platt':
            return self._platt_calibrate(raw_score)
        elif self.method == 'isotonic':
            return self._isotonic_calibrate(raw_score)
        elif self.method == 'beta':
            return self._beta_calibrate(raw_score)
        else:
            return raw_score
    
    def _platt_calibrate(self, score: float) -> float:
        """Platt scaling (sigmoid) calibration"""
        if self._platt_a is None or self._platt_b is None:
            self._fit_platt()
        
        if self._platt_a is None:
            return score
        
        # f(x) = 1 / (1 + exp(A*x + B))
        logit = self._platt_a * score + self._platt_b
        # Clip to avoid overflow
        logit = np.clip(logit, -100, 100)
        calibrated = 1.0 / (1.0 + np.exp(-logit))
        
        return float(calibrated)
    
    def _fit_platt(self):
        """Fit Platt scaling parameters"""
        if len(self.calibration_data) < 10:
            return
        
        scores = [p for p, _ in self.calibration_data]
        labels = [a for _, a in self.calibration_data]
        
        # Simple logistic regression approximation
        # Convert scores to logits
        logits = [np.log(p / (1 - p + 1e-10)) for p in scores]
        
        # Linear regression
        mean_logit = np.mean(logits)
        mean_label = np.mean(labels)
        
        # Calculate slope
        numerator = sum((l - mean_label) * (log - mean_logit) for l, log in zip(labels, logits))
        denominator = sum((log - mean_logit) ** 2 for log in logits)
        
        if denominator > 0:
            self._platt_a = numerator / denominator
            self._platt_b = mean_label - self._platt_a * mean_logit
    
    def _isotonic_calibrate(self, score: float) -> float:
        """Isotonic regression calibration"""
        if self._isotonic_model is None and len(self.calibration_data) >= 50:
            self._fit_isotonic()
        
        if self._isotonic_model is None:
            return score
        
        # Isotonic regression expects 1D input
        calibrated = self._isotonic_model.predict([[score]])[0]
        return float(np.clip(calibrated, 0.01, 0.99))
    
    def _fit_isotonic(self):
        """Fit isotonic regression model"""
        scores = [[p] for p, _ in self.calibration_data]
        labels = [a for _, a in self.calibration_data]
        
        self._isotonic_model = IsotonicRegression(out_of_bounds='clip')
        self._isotonic_model.fit(scores, labels)
    
    def _beta_calibrate(self, score: float) -> float:
        """Beta distribution calibration"""
        if len(self.calibration_data) >= 50:
            self._fit_beta()
        
        # Beta CDF calibration
        calibrated = special.betainc(self._alpha, self._beta, score)
        return float(np.clip(calibrated, 0.01, 0.99))
    
    def _fit_beta(self):
        """Fit beta distribution parameters"""
        scores = [p for p, _ in self.calibration_data]
        labels = [a for _, a in self.calibration_data]
        
        # Method of moments for beta distribution
        mean = np.mean(scores)
        var = np.var(scores)
        
        if var < mean * (1 - mean):
            # Beta parameters
            self._alpha = mean * (mean * (1 - mean) / var - 1)
            self._beta = (1 - mean) * (mean * (1 - mean) / var - 1)
    
    def get_calibration_metrics(self) -> Dict[str, Any]:
        """Get calibration performance metrics"""
        if len(self.calibration_data) < 10:
            return {"status": "insufficient_data", "points": len(self.calibration_data)}
        
        predicted = [p for p, _ in self.calibration_data]
        actual = [a for _, a in self.calibration_data]
        
        # Brier score
        brier = np.mean([(p - a) ** 2 for p, a in zip(predicted, actual)])
        
        # ECE (Expected Calibration Error) - simplified
        n_bins = 10
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        
        for i in range(n_bins):
            bin_mask = (np.array(predicted) >= bin_boundaries[i]) & (np.array(predicted) < bin_boundaries[i + 1])
            if np.sum(bin_mask) > 0:
                bin_accuracy = np.mean(np.array(actual)[bin_mask])
                bin_confidence = np.mean(np.array(predicted)[bin_mask])
                ece += np.abs(bin_accuracy - bin_confidence) * np.sum(bin_mask)
        
        ece /= len(predicted)
        
        return {
            "method": self.method,
            "calibration_points": len(self.calibration_data),
            "brier_score": float(brier),
            "ece": float(ece),
            "mean_predicted": float(np.mean(predicted)),
            "mean_actual": float(np.mean(actual))
        }
    
    def reset(self):
        """Reset calibration data"""
        self.calibration_data = []
        self._platt_a = None
        self._platt_b = None
        self._isotonic_model = None
