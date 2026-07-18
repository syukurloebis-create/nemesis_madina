"""
Drift Monitor
Memonitor performance drift model AI
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
import logging

from .model_registry import ModelVersion, ModelRegistry, model_registry

logger = logging.getLogger(__name__)


@dataclass
class DriftReport:
    """Laporan drift"""
    model_id: str
    model_name: str
    version: str
    drift_score: float
    threshold: float
    is_drifting: bool
    metric_changes: Dict[str, float]
    detected_at: datetime = field(default_factory=datetime.now)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "version": self.version,
            "drift_score": self.drift_score,
            "threshold": self.threshold,
            "is_drifting": self.is_drifting,
            "metric_changes": self.metric_changes,
            "detected_at": self.detected_at.isoformat(),
            "recommendations": self.recommendations
        }


class DriftMonitor:
    """
    Drift Monitor
    Memonitor dan mendeteksi drift pada model
    """

    def __init__(self):
        self.drift_history: Dict[str, List[DriftReport]] = {}
        self.metric_history: Dict[str, Dict[str, List[float]]] = {}
        self.drift_threshold = 0.1

    def check_drift(
        self,
        model_id: str,
        current_metrics: Dict[str, float],
        baseline_metrics: Optional[Dict[str, float]] = None
    ) -> DriftReport:
        """
        Check for drift in model performance
        """
        model = model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")

        if not baseline_metrics:
            baseline_metrics = {
                "accuracy": model.test_accuracy,
                "precision": model.precision,
                "recall": model.recall,
                "f1": model.f1_score,
                "roc_auc": model.roc_auc
            }

        # Calculate drift score
        drift_score, metric_changes = self._calculate_drift_score(
            baseline_metrics, current_metrics
        )

        is_drifting = drift_score > self.drift_threshold

        # Generate recommendations
        recommendations = self._generate_recommendations(
            metric_changes, is_drifting
        )

        report = DriftReport(
            model_id=model_id,
            model_name=model.model_name,
            version=model.version,
            drift_score=drift_score,
            threshold=self.drift_threshold,
            is_drifting=is_drifting,
            metric_changes=metric_changes,
            recommendations=recommendations
        )

        # Store history
        if model_id not in self.drift_history:
            self.drift_history[model_id] = []
        self.drift_history[model_id].append(report)

        # Update model last drift check
        if model_id in model_registry.models:
            model_registry.models[model_id].last_drift_check = datetime.now()

        logger.info(f"Drift check completed for {model.model_name} v{model.version}: drift={drift_score:.3f}")
        return report

    def _calculate_drift_score(
        self,
        baseline: Dict[str, float],
        current: Dict[str, float]
    ) -> tuple[float, Dict[str, float]]:
        """Calculate drift score between baseline and current metrics"""
        changes = {}
        total_change = 0

        for key in baseline:
            if key in current:
                change = abs(current[key] - baseline[key])
                changes[key] = change
                total_change += change

        # Normalize drift score
        max_possible = len(baseline)
        drift_score = total_change / max_possible if max_possible > 0 else 0

        return drift_score, changes

    def _generate_recommendations(
        self,
        changes: Dict[str, float],
        is_drifting: bool
    ) -> List[str]:
        """Generate recommendations based on drift"""
        recommendations = []

        if not is_drifting:
            recommendations.append("Model performance is stable")

        if changes.get("accuracy", 0) > 0.05:
            recommendations.append("Accuracy dropped significantly. Consider retraining")

        if changes.get("precision", 0) > 0.05:
            recommendations.append("Precision dropped. Check false positives")

        if changes.get("recall", 0) > 0.05:
            recommendations.append("Recall dropped. Check false negatives")

        if changes.get("f1", 0) > 0.05:
            recommendations.append("F1 score dropped. Overall performance degradation")

        if not recommendations and not is_drifting:
            recommendations.append("No action needed")

        return recommendations

    def get_drift_history(self, model_id: str) -> List[DriftReport]:
        """Get drift history for a model"""
        return self.drift_history.get(model_id, [])

    def get_recent_drifts(self, days: int = 30) -> List[DriftReport]:
        """Get recent drift reports"""
        cutoff = datetime.now() - timedelta(days=days)
        reports = []
        for history in self.drift_history.values():
            for report in history:
                if report.detected_at >= cutoff and report.is_drifting:
                    reports.append(report)
        return sorted(reports, key=lambda x: x.detected_at, reverse=True)

    def get_model_health(self, model_id: str) -> Dict[str, Any]:
        """Get model health status"""
        model = model_registry.get_model(model_id)
        if not model:
            return {"error": "Model not found"}

        recent_drifts = [r for r in self.get_drift_history(model_id) if r.is_drifting]
        last_drift = recent_drifts[-1] if recent_drifts else None

        return {
            "model_name": model.model_name,
            "version": model.version,
            "status": model.status.value,
            "drift_monitoring_enabled": model.drift_monitoring_enabled,
            "last_drift_check": model.last_drift_check.isoformat() if model.last_drift_check else None,
            "total_drifts": len(recent_drifts),
            "last_drift": last_drift.to_dict() if last_drift else None,
            "health_score": max(0, 100 - len(recent_drifts) * 10)
        }


# Singleton instance
drift_monitor = DriftMonitor()