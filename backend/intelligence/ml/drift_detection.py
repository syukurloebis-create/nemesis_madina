"""
Drift Detection - Monitor ML Model Drift
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import deque
import numpy as np
from scipy import stats


class DataDriftDetector:
    """Detect data drift in model inputs"""
    
    def __init__(self, window_size: int = 1000, threshold: float = 0.05):
        self.window_size = window_size
        self.threshold = threshold
        self.reference_distribution: Dict[str, np.ndarray] = {}
        self.current_window: Dict[str, deque] = {}
    
    def set_reference(self, feature_name: str, data: List[float]):
        """Set reference distribution for a feature"""
        self.reference_distribution[feature_name] = np.array(data)
        self.current_window[feature_name] = deque(maxlen=self.window_size)
    
    def add_sample(self, feature_name: str, value: float):
        """Add sample to current window"""
        if feature_name not in self.current_window:
            self.current_window[feature_name] = deque(maxlen=self.window_size)
        self.current_window[feature_name].append(value)
    
    def detect_drift(self, feature_name: str) -> Dict[str, Any]:
        """Detect drift for a feature using KS test"""
        if feature_name not in self.reference_distribution:
            return {"drift_detected": False, "reason": "No reference distribution"}
        
        current = list(self.current_window.get(feature_name, []))
        if len(current) < 100:
            return {"drift_detected": False, "reason": "Insufficient samples"}
        
        # Kolmogorov-Smirnov test
        ks_statistic, p_value = stats.ks_2samp(
            self.reference_distribution[feature_name],
            np.array(current)
        )
        
        drift_detected = p_value < self.threshold
        
        return {
            "drift_detected": drift_detected,
            "feature": feature_name,
            "ks_statistic": float(ks_statistic),
            "p_value": float(p_value),
            "threshold": self.threshold,
            "reference_mean": float(np.mean(self.reference_distribution[feature_name])),
            "current_mean": float(np.mean(current)),
            "reference_std": float(np.std(self.reference_distribution[feature_name])),
            "current_std": float(np.std(current))
        }
    
    def detect_all_drifts(self) -> List[Dict[str, Any]]:
        """Detect drift for all features"""
        results = []
        for feature in self.reference_distribution.keys():
            result = self.detect_drift(feature)
            if result["drift_detected"]:
                results.append(result)
        return results
    
    def get_drift_report(self) -> str:
        """Generate drift report"""
        results = self.detect_all_drifts()
        
        report = []
        report.append("=" * 60)
        report.append("DATA DRIFT REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Total features monitored: {len(self.reference_distribution)}")
        report.append(f"Drifts detected: {len(results)}")
        report.append("")
        
        for result in results:
            report.append(f"Feature: {result['feature']}")
            report.append(f"  KS Statistic: {result['ks_statistic']:.4f}")
            report.append(f"  P-value: {result['p_value']:.4f}")
            report.append(f"  Mean shift: {result['current_mean'] - result['reference_mean']:.4f}")
            report.append("")
        
        return "\n".join(report)


class ConceptDriftDetector:
    """Detect concept drift in model predictions"""
    
    def __init__(self, window_size: int = 500):
        self.window_size = window_size
        self.predictions: deque = deque(maxlen=window_size)
        self.actuals: deque = deque(maxlen=window_size)
    
    def add_prediction(self, predicted: float, actual: Optional[float] = None):
        """Add prediction to window"""
        self.predictions.append(predicted)
        if actual is not None:
            self.actuals.append(actual)
    
    def detect_performance_drift(self) -> Dict[str, Any]:
        """Detect drift in model performance"""
        if len(self.predictions) < 100:
            return {"drift_detected": False, "reason": "Insufficient predictions"}
        
        # Split into two halves
        mid = len(self.predictions) // 2
        first_half = list(self.predictions)[:mid]
        second_half = list(self.predictions)[mid:]
        
        if len(first_half) < 50 or len(second_half) < 50:
            return {"drift_detected": False, "reason": "Insufficient data"}
        
        # Compare distributions
        ks_statistic, p_value = stats.ks_2samp(first_half, second_half)
        
        drift_detected = p_value < 0.05
        
        return {
            "drift_detected": drift_detected,
            "ks_statistic": float(ks_statistic),
            "p_value": float(p_value),
            "first_half_mean": float(np.mean(first_half)),
            "second_half_mean": float(np.mean(second_half))
        }
    
    def get_performance_trend(self) -> Dict[str, Any]:
        """Get performance trend over time"""
        if len(self.predictions) < 10:
            return {"trend": "insufficient_data"}
        
        values = list(self.predictions)
        # Simple linear regression for trend
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        
        if slope > 0.01:
            trend = "increasing"
        elif slope < -0.01:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "slope": float(slope),
            "current_mean": float(np.mean(values[-100:])) if len(values) >= 100 else float(np.mean(values)),
            "overall_mean": float(np.mean(values))
        }
