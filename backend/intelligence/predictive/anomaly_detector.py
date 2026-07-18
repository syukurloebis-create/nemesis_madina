"""
Anomaly Detection
Deteksi anomaly dalam data
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
from scipy import stats
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class AnomalyResult:
    """Hasil anomaly detection"""
    case_id: str
    is_anomaly: bool
    score: float
    severity: str
    explanation: str
    detected_at: datetime = field(default_factory=datetime.now)
    features: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "is_anomaly": self.is_anomaly,
            "score": self.score,
            "severity": self.severity,
            "explanation": self.explanation,
            "detected_at": self.detected_at.isoformat(),
            "features": self.features
        }


class AnomalyDetector:
    """
    Anomaly Detection Engine
    Mendeteksi anomaly dalam data menggunakan berbagai metode
    """

    def __init__(self):
        self.history: Dict[str, deque] = {}
        self.max_history = 1000
        self.threshold = 3.0  # Number of standard deviations

    def detect(
        self,
        case_id: str,
        data: Dict[str, Any],
        features: Optional[List[str]] = None
    ) -> AnomalyResult:
        """
        Detect anomaly in data
        """
        if features is None:
            features = ['risk_score', 'fraud_score', 'evidence_trust', 'graph_risk']

        # Extract feature values
        feature_values = {k: data.get(k, 0) for k in features}

        # Calculate anomaly score
        anomaly_score, explanation = self._calculate_anomaly_score(case_id, feature_values)

        # Determine severity
        severity = self._get_severity(anomaly_score)

        return AnomalyResult(
            case_id=case_id,
            is_anomaly=anomaly_score > self.threshold,
            score=anomaly_score,
            severity=severity,
            explanation=explanation,
            features=feature_values
        )

    def _calculate_anomaly_score(
        self,
        case_id: str,
        feature_values: Dict[str, float]
    ) -> Tuple[float, str]:
        """
        Calculate anomaly score using multiple methods
        """
        scores = []
        explanations = []

        # 1. Z-score method
        z_score, z_explanation = self._z_score_method(case_id, feature_values)
        scores.append(z_score)
        explanations.append(z_explanation)

        # 2. IQR method
        iqr_score, iqr_explanation = self._iqr_method(case_id, feature_values)
        scores.append(iqr_score)
        explanations.append(iqr_explanation)

        # 3. Mahalanobis distance (simplified)
        mahalanobis_score, mahalanobis_explanation = self._mahalanobis_method(case_id, feature_values)
        scores.append(mahalanobis_score)
        explanations.append(mahalanobis_explanation)

        # Combine scores
        combined_score = np.mean(scores)

        # Get best explanation
        best_explanation = explanations[np.argmax(scores)]

        return combined_score, best_explanation

    def _z_score_method(
        self,
        case_id: str,
        feature_values: Dict[str, float]
    ) -> Tuple[float, str]:
        """Z-score anomaly detection"""
        max_z = 0
        max_feature = ""

        for feature, value in feature_values.items():
            # Get historical values
            historical = self._get_history(case_id, feature)

            if historical and len(historical) > 1:
                mean = np.mean(historical)
                std = np.std(historical)
                if std > 0:
                    z = abs(value - mean) / std
                    if z > max_z:
                        max_z = z
                        max_feature = feature

        return max_z, f"Z-score anomaly: {max_feature} is {max_z:.2f} std deviations from mean"

    def _iqr_method(
        self,
        case_id: str,
        feature_values: Dict[str, float]
    ) -> Tuple[float, str]:
        """IQR anomaly detection"""
        max_score = 0
        max_feature = ""

        for feature, value in feature_values.items():
            historical = self._get_history(case_id, feature)

            if historical and len(historical) > 3:
                q1 = np.percentile(historical, 25)
                q3 = np.percentile(historical, 75)
                iqr = q3 - q1

                if iqr > 0:
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr

                    if value < lower_bound or value > upper_bound:
                        score = min(abs(value - q3) / iqr, abs(q1 - value) / iqr)
                        if score > max_score:
                            max_score = score
                            max_feature = feature

        return max_score, f"IQR anomaly: {max_feature} is outside 1.5 IQR range"

    def _mahalanobis_method(
        self,
        case_id: str,
        feature_values: Dict[str, float]
    ) -> Tuple[float, str]:
        """Simplified Mahalanobis distance"""
        # Use simplified version
        values = list(feature_values.values())
        if not values:
            return 0, "No values to analyze"

        # Calculate normalized distance
        mean = np.mean(values)
        std = np.std(values)
        if std > 0:
            distance = abs(values[0] - mean) / std
            return distance, f"Mahalanobis distance: {distance:.2f}"

        return 0, "Insufficient data for Mahalanobis"

    def _get_history(self, case_id: str, feature: str) -> List[float]:
        """Get historical values for a feature"""
        key = f"{case_id}_{feature}"
        if key not in self.history:
            return []
        return list(self.history[key])

    def update_history(self, case_id: str, feature_values: Dict[str, float]) -> None:
        """Update historical data"""
        for feature, value in feature_values.items():
            key = f"{case_id}_{feature}"
            if key not in self.history:
                self.history[key] = deque(maxlen=self.max_history)
            self.history[key].append(value)

    def _get_severity(self, score: float) -> str:
        """Get severity based on score"""
        if score > 5.0:
            return "CRITICAL"
        elif score > 3.5:
            return "HIGH"
        elif score > 2.5:
            return "MEDIUM"
        return "LOW"


# Singleton instance
anomaly_detector = AnomalyDetector()