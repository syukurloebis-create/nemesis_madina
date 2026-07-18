"""
Performance Tuning
Monitoring dan optimasi performa
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import time
import logging
import threading

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Metric performa"""
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    threshold: Optional[float] = None


@dataclass
class PerformanceAlert:
    """Alert performa"""
    metric_name: str
    current_value: float
    threshold: float
    severity: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)


class PerformanceMonitor:
    """
    Performance Monitoring
    Monitor dan optimasi performa sistem
    """

    def __init__(self):
        self.metrics: Dict[str, deque] = {}
        self.alerts: List[PerformanceAlert] = []
        self.max_history = 1000
        self.thresholds = {
            "api_response_time": 200,  # ms
            "db_query_time": 100,      # ms
            "ai_inference_time": 500,  # ms
            "graph_query_time": 200,   # ms
            "memory_usage": 80,        # %
            "cpu_usage": 70,           # %
        }
        self._alert_callbacks = []

    def record(
        self,
        name: str,
        value: float,
        unit: str = "ms",
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            tags=tags or {}
        )

        if name not in self.metrics:
            self.metrics[name] = deque(maxlen=self.max_history)
        self.metrics[name].append(metric)

        # Check threshold
        if name in self.thresholds and value > self.thresholds[name]:
            self._check_alert(metric)

    def _check_alert(self, metric: PerformanceMetric) -> None:
        """Check if metric exceeds threshold"""
        threshold = self.thresholds.get(metric.name)
        if threshold is None:
            return

        # Check recent metrics (last 5)
        recent = list(self.metrics[metric.name])[-5:]
        if len(recent) < 3:
            return

        # Alert if consistently above threshold
        above_count = sum(1 for m in recent if m.value > threshold)
        if above_count >= 3:
            alert = PerformanceAlert(
                metric_name=metric.name,
                current_value=metric.value,
                threshold=threshold,
                severity="warning",
                message=f"Performance degradation detected: {metric.name} = {metric.value}{metric.unit} (threshold: {threshold}{metric.unit})",
                timestamp=datetime.now()
            )
            self.alerts.append(alert)

            # Call callbacks
            for callback in self._alert_callbacks:
                callback(alert)

    def get_metric(self, name: str) -> List[PerformanceMetric]:
        """Get metric history"""
        return list(self.metrics.get(name, []))

    def get_latest(self, name: str) -> Optional[PerformanceMetric]:
        """Get latest metric value"""
        metrics = self.metrics.get(name, [])
        return metrics[-1] if metrics else None

    def get_average(self, name: str, minutes: int = 5) -> float:
        """Get average metric value over last N minutes"""
        metrics = self.metrics.get(name, [])
        if not metrics:
            return 0

        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent = [m for m in metrics if m.timestamp >= cutoff]

        if not recent:
            return 0

        return sum(m.value for m in recent) / len(recent)

    def get_percentile(self, name: str, percentile: float, minutes: int = 5) -> float:
        """Get percentile metric value"""
        metrics = self.metrics.get(name, [])
        if not metrics:
            return 0

        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent = [m.value for m in metrics if m.timestamp >= cutoff]

        if not recent:
            return 0

        sorted_values = sorted(recent)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[index] if index < len(sorted_values) else sorted_values[-1]

    def set_threshold(self, name: str, threshold: float) -> None:
        """Set threshold for metric"""
        self.thresholds[name] = threshold

    def get_thresholds(self) -> Dict[str, float]:
        """Get all thresholds"""
        return self.thresholds.copy()

    def get_alerts(self, severity: Optional[str] = None) -> List[PerformanceAlert]:
        """Get alerts"""
        if severity:
            return [a for a in self.alerts if a.severity == severity]
        return self.alerts

    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "alerts": len(self.alerts)
        }

        for name in self.thresholds:
            latest = self.get_latest(name)
            avg = self.get_average(name, 5)
            p95 = self.get_percentile(name, 95, 5)

            status["metrics"][name] = {
                "latest": latest.value if latest else None,
                "unit": latest.unit if latest else "ms",
                "avg_5min": avg,
                "p95": p95,
                "threshold": self.thresholds.get(name)
            }

        return status

    def register_alert_callback(self, callback) -> None:
        """Register alert callback"""
        self._alert_callbacks.append(callback)


# Singleton instance
performance_monitor = PerformanceMonitor()