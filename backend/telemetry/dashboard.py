"""
Dashboard - Metrics Dashboard API
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from backend.telemetry.metrics import metrics_registry


class MetricsDashboard:
    """Metrics dashboard for visualization"""
    
    def __init__(self):
        self.registry = metrics_registry
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": self._get_uptime(),
            "metrics": self.get_metrics_summary()
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        all_metrics = self.registry.get_all_metrics()
        
        summary = {
            "counters": {},
            "gauges": {},
            "histograms": {}
        }
        
        for name, metric in all_metrics.items():
            if metric["type"] == "counter":
                summary["counters"][name] = metric["value"]
            elif metric["type"] == "gauge":
                summary["gauges"][name] = metric["value"]
            elif metric["type"] == "histogram":
                summary["histograms"][name] = metric["stats"]
        
        return summary
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance-related metrics"""
        all_metrics = self.registry.get_all_metrics()
        
        performance = {
            "event_processing": {
                "avg_ms": 0,
                "p95_ms": 0,
                "total": 0
            },
            "api_latency": {
                "avg_ms": 0,
                "p95_ms": 0
            },
            "websocket": {
                "connections": 0,
                "messages_per_sec": 0
            }
        }
        
        # Extract from histograms
        for name, metric in all_metrics.items():
            if metric["type"] == "histogram":
                if "event" in name.lower():
                    performance["event_processing"]["avg_ms"] = metric["stats"].get("avg", 0)
                    performance["event_processing"]["p95_ms"] = metric["stats"].get("p95", 0)
                elif "api" in name.lower():
                    performance["api_latency"]["avg_ms"] = metric["stats"].get("avg", 0)
                    performance["api_latency"]["p95_ms"] = metric["stats"].get("p95", 0)
        
        return performance
    
    def _get_uptime(self) -> float:
        """Get system uptime (simplified)"""
        # In production, track actual start time
        return 3600.0  # Placeholder
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        return {
            "health": self.get_system_health(),
            "metrics": self.get_metrics_summary(),
            "performance": self.get_performance_metrics(),
            "timestamp": datetime.now().isoformat()
        }


# Global dashboard instance
dashboard = MetricsDashboard()


def get_dashboard_data() -> Dict[str, Any]:
    """Get dashboard data for API endpoint"""
    return dashboard.get_dashboard_data()
