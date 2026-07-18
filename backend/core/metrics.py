"""
Metrics dasar untuk monitoring.
"""

import logging
from collections import defaultdict
from typing import Dict, Any
from dataclasses import dataclass, field
from backend.core.timer import measure_time as measure_operation


@dataclass
class CounterMetric:
    """Counter metric."""
    name: str
    value: int = 0
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class GaugeMetric:
    """Gauge metric."""
    name: str
    value: float = 0
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsRegistry:
    """
    Registry untuk metrics.
    """

    def __init__(self):
        self._counters: Dict[str, CounterMetric] = {}
        self._gauges: Dict[str, GaugeMetric] = {}

    def counter(self, name: str, labels: Dict[str, str] = None) -> CounterMetric:
        """Dapatkan atau buat counter."""
        key = name
        if labels:
            key = f"{name}_{'_'.join(f'{k}={v}' for k, v in sorted(labels.items()))}"
        if key not in self._counters:
            self._counters[key] = CounterMetric(name=name, labels=labels or {})
        return self._counters[key]

    def gauge(self, name: str, labels: Dict[str, str] = None) -> GaugeMetric:
        """Dapatkan atau buat gauge."""
        key = name
        if labels:
            key = f"{name}_{'_'.join(f'{k}={v}' for k, v in sorted(labels.items()))}"
        if key not in self._gauges:
            self._gauges[key] = GaugeMetric(name=name, labels=labels or {})
        return self._gauges[key]

    def inc_counter(self, name: str, labels: Dict[str, str] = None, value: int = 1):
        """Increment counter."""
        counter = self.counter(name, labels)
        counter.value += value

    def set_gauge(self, name: str, labels: Dict[str, str] = None, value: float = 0):
        """Set gauge value."""
        gauge = self.gauge(name, labels)
        gauge.value = value

    def get_metrics(self) -> Dict[str, Any]:
        """Dapatkan semua metrics."""
        return {
            "counters": {
                k: v.value for k, v in self._counters.items()
            },
            "gauges": {
                k: v.value for k, v in self._gauges.items()
            }
        }


# Singleton registry
_metrics_registry = MetricsRegistry()


def get_metrics_registry() -> MetricsRegistry:
    """Dapatkan metrics registry singleton."""
    return _metrics_registry


# ============================================================
# Helper functions untuk metrics yang sering digunakan
# ============================================================

def record_dashboard_request(case_id: str, success: bool = True):
    """Record dashboard request metric."""
    registry = get_metrics_registry()
    registry.inc_counter(
        "dashboard_requests",
        labels={"case_id": case_id[:8] if case_id else "unknown"}
    )
    if not success:
        registry.inc_counter(
            "dashboard_errors",
            labels={"case_id": case_id[:8] if case_id else "unknown"}
        )


def record_finding_created(case_id: str, finding_type: str):
    """Record finding created metric."""
    registry = get_metrics_registry()
    registry.inc_counter(
        "finding_created",
        labels={"finding_type": finding_type}
    )
    registry.inc_counter(
        "findings_by_case",
        labels={"case_id": case_id[:8] if case_id else "unknown"}
    )


def record_cache_hit(cache_name: str):
    """Record cache hit metric."""
    registry = get_metrics_registry()
    registry.inc_counter(
        "cache_hit",
        labels={"cache": cache_name}
    )


def record_cache_miss(cache_name: str):
    """Record cache miss metric."""
    registry = get_metrics_registry()
    registry.inc_counter(
        "cache_miss",
        labels={"cache": cache_name}
    )


def record_lifecycle_event(event_type: str):
    """Record lifecycle event metric."""
    registry = get_metrics_registry()
    registry.inc_counter(
        "lifecycle_events",
        labels={"event": event_type}
    )


def record_db_operation(operation: str, success: bool = True):
    """Record database operation metric."""
    registry = get_metrics_registry()
    registry.inc_counter(
        "db_operations",
        labels={"operation": operation, "success": str(success)}
    )