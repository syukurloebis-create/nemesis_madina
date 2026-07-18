"""
Model Calibration
Kalibrasi model untuk prediksi yang akurat
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.calibration import calibration_curve
import logging

logger = logging.getLogger(__name__)


@dataclass
class CalibrationResult:
    """Hasil kalibrasi"""
    model_name: str
    calibration_score: float
    reliability_diagram: Dict[str, List[float]]
    brier_score: float
    ece: float  # Expected Calibration Error
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "calibration_score": self.calibration_score,
            "reliability_diagram": self.reliability_diagram,
            "brier_score": self.brier_score,
            "ece": self.ece,
            "timestamp": self.timestamp.isoformat()
        }


class ModelCalibrator:
    """
    Model Calibration Engine
    Mengkalibrasi probabilitas prediksi
    """

    def __init__(self):
        self.calibration_model = None
        self.is_calibrated = False

    def calibrate(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        n_bins: int = 10
    ) -> CalibrationResult:
        """
        Calibrate model probabilities
        """
        # Fit isotonic regression
        calibrator = IsotonicRegression(
            y_min=0.0,
            y_max=1.0,
            increasing=True,
            out_of_bounds='clip'
        )
        calibrator.fit(y_prob, y_true)

        self.calibration_model = calibrator
        self.is_calibrated = True

        # Calculate calibration metrics
        fraction_positive, mean_predicted = calibration_curve(
            y_true, y_prob, n_bins=n_bins, strategy='uniform'
        )

        # Calculate calibration score
        calibration_score = np.corrcoef(fraction_positive, mean_predicted)[0, 1] \
            if len(fraction_positive) > 1 else 0

        # Calculate Brier score
        brier_score = np.mean((y_prob - y_true) ** 2)

        # Calculate ECE
        ece = self._calculate_ece(y_true, y_prob, n_bins)

        return CalibrationResult(
            model_name="isotonic_calibration",
            calibration_score=calibration_score,
            reliability_diagram={
                "fraction_positive": fraction_positive.tolist(),
                "mean_predicted": mean_predicted.tolist()
            },
            brier_score=brier_score,
            ece=ece
        )

    def _calculate_ece(self, y_true: np.ndarray, y_prob: np.ndarray, n_bins: int) -> float:
        """Calculate Expected Calibration Error"""
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_indices = np.digitize(y_prob, bin_boundaries, right=False)

        ece = 0.0
        for i in range(1, n_bins + 1):
            mask = bin_indices == i
            if np.sum(mask) > 0:
                bin_accuracy = np.mean(y_true[mask])
                bin_confidence = np.mean(y_prob[mask])
                ece += np.abs(bin_accuracy - bin_confidence) * np.mean(mask)

        return ece / len(y_prob) * 100

    def calibrate_probability(self, probability: float) -> float:
        """Calibrate a single probability"""
        if not self.is_calibrated or self.calibration_model is None:
            return probability

        calibrated = self.calibration_model.predict([probability])[0]
        return max(0.0, min(1.0, calibrated))

    def calibrate_batch(self, probabilities: List[float]) -> List[float]:
        """Calibrate batch of probabilities"""
        if not self.is_calibrated or self.calibration_model is None:
            return probabilities

        calibrated = self.calibration_model.predict(probabilities)
        return [max(0.0, min(1.0, p)) for p in calibrated]

    def get_calibration_report(self) -> Dict[str, Any]:
        """Get calibration report"""
        return {
            "is_calibrated": self.is_calibrated,
            "calibration_model": "isotonic_regression" if self.is_calibrated else None,
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
model_calibrator = ModelCalibrator()