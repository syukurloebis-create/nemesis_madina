"""
Prometheus Exporter - Export metrics to Prometheus
"""

from typing import Dict, Any
from backend.telemetry.metrics import metrics_registry


class PrometheusExporter:
    """Export metrics in Prometheus format"""
    
    def __init__(self, endpoint: str = "/metrics"):
        self.endpoint = endpoint
        self.registry = metrics_registry
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return self.registry.get_prometheus_format()
    
    def get_endpoint(self) -> str:
        """Get metrics endpoint path"""
        return self.endpoint
    
    def get_metric_families(self) -> Dict[str, Any]:
        """Get metric families for Prometheus client"""
        all_metrics = self.registry.get_all_metrics()
        
        families = {}
        for name, metric in all_metrics.items():
            if metric["type"] == "counter":
                families[name] = {
                    "type": "counter",
                    "help": f"Counter metric {name}",
                    "metrics": [{"labels": {}, "value": metric["value"]}]
                }
            elif metric["type"] == "gauge":
                families[name] = {
                    "type": "gauge",
                    "help": f"Gauge metric {name}",
                    "metrics": [{"labels": {}, "value": metric["value"]}]
                }
            elif metric["type"] == "histogram":
                stats = metric.get("stats", {})
                families[name] = {
                    "type": "histogram",
                    "help": f"Histogram metric {name}",
                    "metrics": [
                        {"labels": {"quantile": "0.5"}, "value": stats.get("p50", 0)},
                        {"labels": {"quantile": "0.9"}, "value": stats.get("p90", 0)},
                        {"labels": {"quantile": "0.95"}, "value": stats.get("p95", 0)},
                        {"labels": {"quantile": "0.99"}, "value": stats.get("p99", 0)}
                    ]
                }
        
        return families


# Global exporter
prometheus_exporter = PrometheusExporter()
