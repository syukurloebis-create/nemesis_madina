# backend/telemetry/metrics_registry.py

from typing import Dict, Any, Optional, List, Union
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import time


class MetricsRegistry:
    """
    Metrics registry with legacy compatibility.

    Production:
        uses prometheus REGISTRY (injected)

    Tests:
        uses isolated CollectorRegistry by default
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        # ✅ Default ke CollectorRegistry baru per instance (test isolation)
        # Production: inject REGISTRY
        self._registry = registry or CollectorRegistry()
        self._metrics: Dict[str, Any] = {}

        # Legacy storage
        self._counter_values: Dict[str, float] = {}
        self._gauge_values: Dict[str, float] = {}
        self._histogram_values: Dict[str, List[float]] = {}

    def reset(self):
        """
        Reset all metrics state for test isolation.

        ✅ Clears legacy storage
        ✅ Clears cached Prometheus objects
        ✅ Replaces CollectorRegistry with a fresh one
        """
        self._counter_values.clear()
        self._gauge_values.clear()
        self._histogram_values.clear()
        self._metrics.clear()
        self._registry = CollectorRegistry()

    # ============================================================
    # HELPERS
    # ============================================================

    @staticmethod
    def _is_numeric(value) -> bool:
        return isinstance(value, (int, float))

    @staticmethod
    def _get_metric_key(metric_type: str, name: str) -> str:
        return f"{metric_type}:{name}"

    def _get_or_create_counter(self, name: str) -> Counter:
        key = self._get_metric_key("counter", name)
        if key not in self._metrics:
            self._metrics[key] = Counter(name, name, registry=self._registry)
        return self._metrics[key]

    def _get_or_create_gauge(self, name: str) -> Gauge:
        key = self._get_metric_key("gauge", name)
        if key not in self._metrics:
            self._metrics[key] = Gauge(name, name, registry=self._registry)
        return self._metrics[key]

    def _get_or_create_histogram(self, name: str) -> Histogram:
        key = self._get_metric_key("histogram", name)
        if key not in self._metrics:
            self._metrics[key] = Histogram(name, name, registry=self._registry)
        return self._metrics[key]

    # ============================================================
    # LEGACY API with Prometheus Sync
    # ============================================================

    def counter(self, name: str, *args, **kwargs) -> Union[None, Counter]:
        """
        Universal counter method.

        Legacy: counter(name, value=1)
        New:    counter(name, description, labels=None)
        """
        # Legacy mode: counter(name, value=1)
        if "value" in kwargs or (len(args) == 1 and self._is_numeric(args[0])):
            value = kwargs.get("value", args[0] if args else 1)

            # ✅ Update legacy storage
            if name not in self._counter_values:
                self._counter_values[name] = 0.0
            self._counter_values[name] += float(value)

            # ✅ Sync to Prometheus
            metric = self._get_or_create_counter(name)
            metric.inc(float(value))

            return None

        # Prometheus mode: counter(name, description, labels=None)
        description = args[0] if args else kwargs.get("description", "")
        labels = args[1] if len(args) > 1 else kwargs.get("labels", [])
        key = self._get_metric_key("counter", name)
        if key not in self._metrics:
            self._metrics[key] = Counter(name, description, labels or [], registry=self._registry)
        return self._metrics[key]

    def gauge(self, name: str, *args, **kwargs) -> Union[None, Gauge]:
        """
        Universal gauge method.

        Legacy: gauge(name, value)
        New:    gauge(name, description, labels=None)
        """
        # Legacy mode: gauge(name, value)
        if len(args) == 1 and self._is_numeric(args[0]):
            value = float(args[0])
            self._gauge_values[name] = value

            # ✅ Sync to Prometheus
            metric = self._get_or_create_gauge(name)
            metric.set(value)

            return None
        if "value" in kwargs:
            value = float(kwargs["value"])
            self._gauge_values[name] = value

            # ✅ Sync to Prometheus
            metric = self._get_or_create_gauge(name)
            metric.set(value)

            return None

        # Prometheus mode: gauge(name, description, labels=None)
        description = args[0] if args else kwargs.get("description", "")
        labels = args[1] if len(args) > 1 else kwargs.get("labels", [])
        key = self._get_metric_key("gauge", name)
        if key not in self._metrics:
            self._metrics[key] = Gauge(name, description, labels or [], registry=self._registry)
        return self._metrics[key]

    def histogram(self, name: str, *args, **kwargs) -> Union[None, Histogram]:
        """
        Universal histogram method.

        Legacy: histogram(name, value)
        New:    histogram(name, description, labels=None, buckets=None)
        """
        # Legacy mode: histogram(name, value)
        if len(args) == 1 and self._is_numeric(args[0]):
            value = float(args[0])
            if name not in self._histogram_values:
                self._histogram_values[name] = []
            self._histogram_values[name].append(value)

            # ✅ Sync to Prometheus
            metric = self._get_or_create_histogram(name)
            metric.observe(value)

            return None
        if "value" in kwargs:
            value = float(kwargs["value"])
            if name not in self._histogram_values:
                self._histogram_values[name] = []
            self._histogram_values[name].append(value)

            # ✅ Sync to Prometheus
            metric = self._get_or_create_histogram(name)
            metric.observe(value)

            return None

        # Prometheus mode: histogram(name, description, labels=None, buckets=None)
        description = args[0] if args else kwargs.get("description", "")
        labels = args[1] if len(args) > 1 else kwargs.get("labels", [])
        buckets = kwargs.get("buckets", None)
        key = self._get_metric_key("histogram", name)
        if key not in self._metrics:
            self._metrics[key] = Histogram(name, description, labels or [], buckets=buckets, registry=self._registry)
        return self._metrics[key]

    # ============================================================
    # GETTERS (Legacy Compatibility)
    # ============================================================

    def get_counter(self, name: str) -> float:
        return self._counter_values.get(name, 0.0)

    def get_gauge(self, name: str) -> float:
        return self._gauge_values.get(name, 0.0)

    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        values = self._histogram_values.get(name, [])
        if not values:
            return {"count": 0, "min": 0.0, "max": 0.0, "sum": 0.0}
        return {
            "count": float(len(values)),
            "min": float(min(values)),
            "max": float(max(values)),
            "sum": float(sum(values)),
        }

    def get_all_metrics(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        result.update(self._counter_values)
        result.update(self._gauge_values)
        for name in self._histogram_values:
            result[name] = self.get_histogram_stats(name)
        return result

    def get_prometheus_format(self) -> str:
        return self.generate_latest().decode('utf-8')

    # ============================================================
    # PROMETHEUS API
    # ============================================================

    async def startup(self):
        pass

    async def shutdown(self):
        pass

    def generate_latest(self) -> bytes:
        from prometheus_client import generate_latest
        return generate_latest(self._registry)