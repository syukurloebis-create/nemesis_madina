#!/usr/bin/env python3
"""
NEMESIS FASE 4 - Enhance ML Modules with Drift Detection and Ensemble
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

ML_DIR = PROJECT_ROOT / "backend" / "intelligence" / "ml"

def create_drift_detection():
    """Create drift_detection.py for model monitoring"""
    print("\n[1/6] Creating drift detection module...")
    
    content = '''"""
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
        
        return "\\n".join(report)


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
'''
    
    file_path = ML_DIR / "drift_detection.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_ensemble():
    """Create ensemble.py for model ensemble"""
    print("\n[2/6] Creating ensemble module...")
    
    content = '''"""
Ensemble Learning - Combine Multiple Models
"""

from typing import List, Dict, Any, Callable, Optional
from collections import defaultdict
import numpy as np


class EnsembleModel:
    """Ensemble of multiple models for improved accuracy"""
    
    def __init__(self, models: List[Dict[str, Any]]):
        """
        models: List of dicts with 'model', 'weight', 'name'
        """
        self.models = models
        self._normalize_weights()
    
    def _normalize_weights(self):
        """Normalize model weights to sum to 1"""
        total = sum(m.get('weight', 1.0) for m in self.models)
        if total > 0:
            for m in self.models:
                m['weight'] = m.get('weight', 1.0) / total
    
    def predict(self, features: Dict[str, float]) -> float:
        """Get weighted average prediction"""
        total_score = 0.0
        
        for model in self.models:
            model_instance = model['model']
            weight = model['weight']
            
            if hasattr(model_instance, 'predict'):
                score = model_instance.predict(features)
            elif hasattr(model_instance, 'compute_score'):
                score = model_instance.compute_score(features)
            else:
                score = 0.5
            
            total_score += score * weight
        
        return min(max(total_score, 0.0), 1.0)
    
    def predict_with_confidence(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Get prediction with confidence interval"""
        predictions = []
        weights = []
        
        for model in self.models:
            model_instance = model['model']
            weight = model['weight']
            
            if hasattr(model_instance, 'predict'):
                score = model_instance.predict(features)
            else:
                score = 0.5
            
            predictions.append(score)
            weights.append(weight)
        
        weighted_score = np.average(predictions, weights=weights)
        
        # Calculate confidence based on agreement
        variance = np.var(predictions)
        confidence = 1.0 - min(variance * 2, 1.0)
        
        return {
            "score": float(weighted_score),
            "confidence": float(confidence),
            "individual_scores": [
                {"model": m.get('name', f"model_{i}"), "score": s}
                for i, (m, s) in enumerate(zip(self.models, predictions))
            ]
        }
    
    def add_model(self, model: Any, weight: float = 1.0, name: str = None):
        """Add a new model to ensemble"""
        self.models.append({
            'model': model,
            'weight': weight,
            'name': name or f"model_{len(self.models)}"
        })
        self._normalize_weights()
    
    def remove_model(self, name: str):
        """Remove a model by name"""
        self.models = [m for m in self.models if m.get('name') != name]
        self._normalize_weights()
    
    def get_weights(self) -> Dict[str, float]:
        """Get current model weights"""
        return {m.get('name', f"model_{i}"): m['weight'] for i, m in enumerate(self.models)}
    
    def set_weights(self, weights: Dict[str, float]):
        """Set custom model weights"""
        for model in self.models:
            name = model.get('name')
            if name in weights:
                model['weight'] = weights[name]
        self._normalize_weights()


class VotingEnsemble:
    """Voting ensemble (majority vote) for classification"""
    
    def __init__(self, models: List[Any], voting: str = 'soft'):
        """
        voting: 'hard' for majority vote, 'soft' for probability average
        """
        self.models = models
        self.voting = voting
    
    def predict(self, features: Dict[str, float]) -> float:
        """Get ensemble prediction"""
        predictions = []
        
        for model in self.models:
            if hasattr(model, 'predict'):
                pred = model.predict(features)
            else:
                pred = 0.5
            predictions.append(pred)
        
        if self.voting == 'hard':
            # Convert to binary and take majority
            binary = [1 if p > 0.5 else 0 for p in predictions]
            majority = sum(binary) / len(binary)
            return majority
        else:
            # Soft voting - average probabilities
            return np.mean(predictions)
    
    def predict_with_agreement(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Get prediction with agreement level"""
        predictions = []
        
        for model in self.models:
            if hasattr(model, 'predict'):
                pred = model.predict(features)
            else:
                pred = 0.5
            predictions.append(pred)
        
        final_score = np.mean(predictions)
        
        # Agreement is 1 - variance
        agreement = 1.0 - min(np.var(predictions) * 2, 1.0)
        
        return {
            "score": float(final_score),
            "agreement": float(agreement),
            "predictions": predictions
        }
'''
    
    file_path = ML_DIR / "ensemble.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_feature_store():
    """Create feature_store.py for feature management"""
    print("\n[3/6] Creating feature store...")
    
    content = '''"""
Feature Store - Centralized Feature Management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json


class FeatureStore:
    """Centralized store for features"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._features: Dict[str, Dict[str, Any]] = {}
        self._feature_history: Dict[str, List[tuple]] = defaultdict(list)
        self._feature_metadata: Dict[str, Dict[str, Any]] = {}
        self._initialized = True
    
    def register_feature(self, name: str, feature_type: str, metadata: Dict[str, Any] = None):
        """Register a new feature"""
        self._feature_metadata[name] = {
            "name": name,
            "type": feature_type,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
    
    def set_feature(self, entity_id: str, feature_name: str, value: Any, timestamp: datetime = None):
        """Set feature value for an entity"""
        if timestamp is None:
            timestamp = datetime.now()
        
        if entity_id not in self._features:
            self._features[entity_id] = {}
        
        self._features[entity_id][feature_name] = value
        self._feature_history[feature_name].append((timestamp, value, entity_id))
        
        # Keep history manageable
        if len(self._feature_history[feature_name]) > 10000:
            self._feature_history[feature_name] = self._feature_history[feature_name][-5000:]
    
    def get_feature(self, entity_id: str, feature_name: str) -> Optional[Any]:
        """Get feature value for an entity"""
        return self._features.get(entity_id, {}).get(feature_name)
    
    def get_features(self, entity_id: str) -> Dict[str, Any]:
        """Get all features for an entity"""
        return self._features.get(entity_id, {}).copy()
    
    def get_feature_history(self, feature_name: str, limit: int = 100) -> List[tuple]:
        """Get historical values for a feature"""
        return self._feature_history.get(feature_name, [])[-limit:]
    
    def get_feature_stats(self, feature_name: str) -> Dict[str, Any]:
        """Get statistics for a feature"""
        history = self.get_feature_history(feature_name, limit=1000)
        if not history:
            return {"error": "No data available"}
        
        values = [v for _, v, _ in history]
        
        return {
            "name": feature_name,
            "count": len(values),
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(min(values)),
            "max": float(max(values)),
            "recent": values[-10:]
        }
    
    def get_entity_vector(self, entity_id: str, feature_names: List[str] = None) -> Dict[str, float]:
        """Get feature vector for an entity"""
        features = self.get_features(entity_id)
        
        if feature_names:
            return {name: features.get(name, 0.0) for name in feature_names}
        return features
    
    def delete_entity_features(self, entity_id: str):
        """Delete all features for an entity"""
        if entity_id in self._features:
            del self._features[entity_id]
    
    def get_all_entities(self) -> List[str]:
        """Get all entity IDs with features"""
        return list(self._features.keys())
    
    def get_feature_metadata(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a feature"""
        return self._feature_metadata.get(feature_name)
    
    def list_features(self) -> List[str]:
        """List all registered features"""
        return list(self._feature_metadata.keys())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall feature store statistics"""
        return {
            "total_entities": len(self._features),
            "total_features": len(self._feature_metadata),
            "features_with_history": len(self._feature_history),
            "total_feature_values": sum(len(v) for v in self._features.values())
        }


import numpy as np  # Add at top
'''
    
    file_path = ML_DIR / "feature_store.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def enhance_anomaly():
    """Enhance anomaly.py with advanced detection"""
    print("\n[4/6] Enhancing anomaly detection...")
    
    content = '''"""
Anomaly Detection - Advanced Anomaly Detection
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from scipy import stats
from collections import deque


class AnomalyDetector:
    """Advanced anomaly detection with multiple methods"""
    
    def __init__(self, threshold: float = 3.0, method: str = 'zscore'):
        self.threshold = threshold
        self.method = method  # zscore, iqr, isolation, mad
        self._history: deque = deque(maxlen=10000)
    
    def detect(self, data: List[float]) -> List[int]:
        """Detect anomalies in time series"""
        if len(data) < 10:
            return []
        
        if self.method == 'zscore':
            return self._detect_zscore(data)
        elif self.method == 'iqr':
            return self._detect_iqr(data)
        elif self.method == 'mad':
            return self._detect_mad(data)
        else:
            return self._detect_zscore(data)
    
    def _detect_zscore(self, data: List[float]) -> List[int]:
        """Z-score based anomaly detection"""
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return []
        
        anomalies = []
        for i, value in enumerate(data):
            z_score = abs(value - mean) / std
            if z_score > self.threshold:
                anomalies.append(i)
        
        return anomalies
    
    def _detect_iqr(self, data: List[float]) -> List[int]:
        """IQR (Interquartile Range) based detection"""
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        return [i for i, v in enumerate(data) if v < lower_bound or v > upper_bound]
    
    def _detect_mad(self, data: List[float]) -> List[int]:
        """Median Absolute Deviation based detection"""
        median = np.median(data)
        mad = np.median([abs(x - median) for x in data])
        
        if mad == 0:
            return []
        
        modified_z_scores = [0.6745 * abs(x - median) / mad for x in data]
        
        return [i for i, z in enumerate(modified_z_scores) if z > self.threshold]
    
    def detect_online(self, value: float) -> Tuple[bool, float]:
        """Online anomaly detection (streaming)"""
        self._history.append(value)
        
        if len(self._history) < 50:
            return False, 0.0
        
        data = list(self._history)
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return False, 0.0
        
        z_score = abs(value - mean) / std
        is_anomaly = z_score > self.threshold
        
        return is_anomaly, float(z_score / self.threshold)
    
    def get_anomaly_score(self, value: float, historical: List[float]) -> float:
        """Get normalized anomaly score"""
        if not historical:
            return 0.0
        
        mean = np.mean(historical)
        std = np.std(historical)
        
        if std == 0:
            return 0.0
        
        z_score = abs(value - mean) / std
        return min(z_score / 5, 1.0)
    
    def get_seasonality_score(self, data: List[float], period: int = 24) -> float:
        """Detect seasonality strength"""
        if len(data) < period * 2:
            return 0.0
        
        # Split into periods
        periods = [data[i:i+period] for i in range(0, len(data) - period, period)]
        
        if len(periods) < 2:
            return 0.0
        
        # Calculate variance within periods and between periods
        within_var = np.mean([np.var(p) for p in periods])
        between_var = np.var([np.mean(p) for p in periods])
        
        if within_var == 0:
            return 1.0 if between_var > 0 else 0.0
        
        seasonality = between_var / (between_var + within_var)
        return float(seasonality)
    
    def update_threshold(self, new_threshold: float):
        """Update detection threshold"""
        self.threshold = new_threshold
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics"""
        return {
            "method": self.method,
            "threshold": self.threshold,
            "history_size": len(self._history)
        }
'''
    
    file_path = ML_DIR / "anomaly.py"
    file_path.write_text(content)
    print(f"  [OK] Enhanced: {file_path}")
    return True

def enhance_scoring():
    """Enhance scoring.py with advanced scoring"""
    print("\n[5/6] Enhancing risk scoring...")
    
    content = '''"""
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
'''
    
    file_path = ML_DIR / "scoring.py"
    file_path.write_text(content)
    print(f"  [OK] Enhanced: {file_path}")
    return True

def enhance_calibration():
    """Enhance calibration.py with advanced calibration"""
    print("\n[6/6] Enhancing confidence calibration...")
    
    content = '''"""
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
'''
    
    file_path = ML_DIR / "calibration.py"
    file_path.write_text(content)
    print(f"  [OK] Enhanced: {file_path}")
    return True

def main():
    print("\n" + "="*60)
    print("FASE 4: ENHANCE ML MODULES")
    print("="*60)
    
    create_drift_detection()
    create_ensemble()
    create_feature_store()
    enhance_anomaly()
    enhance_scoring()
    enhance_calibration()
    
    print("\n" + "="*60)
    print("[OK] ML modules enhanced")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())