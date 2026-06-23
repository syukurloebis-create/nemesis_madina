"""
Grafana Exporter - Format metrics for Grafana
"""

from typing import Dict, Any, List
from telemetry.metrics import metrics_registry


class GrafanaExporter:
    """Export metrics in Grafana Live format"""
    
    def __init__(self):
        self.registry = metrics_registry
    
    def get_dataframe_format(self) -> List[Dict[str, Any]]:
        """Get metrics in DataFrame format for Grafana"""
        all_metrics = self.registry.get_all_metrics()
        
        dataframes = []
        
        for name, metric in all_metrics.items():
            if metric["type"] == "counter":
                dataframes.append({
                    "target": name,
                    "datapoints": [[metric["value"], datetime.now().timestamp() * 1000]]
                })
            elif metric["type"] == "gauge":
                dataframes.append({
                    "target": name,
                    "datapoints": [[metric["value"], datetime.now().timestamp() * 1000]]
                })
        
        return dataframes
    
    def get_table_format(self) -> Dict[str, Any]:
        """Get metrics in Table format for Grafana"""
        all_metrics = self.registry.get_all_metrics()
        
        columns = [{"text": "Metric", "type": "string"}, {"text": "Value", "type": "number"}, {"text": "Type", "type": "string"}]
        rows = []
        
        for name, metric in all_metrics.items():
            if metric["type"] == "counter":
                rows.append([name, metric["value"], "counter"])
            elif metric["type"] == "gauge":
                rows.append([name, metric["value"], "gauge"])
            elif metric["type"] == "histogram":
                stats = metric.get("stats", {})
                rows.append([f"{name}_avg", stats.get("avg", 0), "histogram"])
                rows.append([f"{name}_p95", stats.get("p95", 0), "histogram"])
        
        return {"columns": columns, "rows": rows, "type": "table"}
    
    def get_annotations(self) -> List[Dict[str, Any]]:
        """Get annotations for Grafana"""
        from telemetry.alerts import alert_manager
        
        alerts = alert_manager.get_alert_history(limit=50)
        
        annotations = []
        for alert in alerts:
            annotations.append({
                "annotation": {
                    "title": alert["name"],
                    "text": alert["message"],
                    "tags": [alert["severity"]]
                },
                "time": int(datetime.fromisoformat(alert["created_at"]).timestamp() * 1000)
            })
        
        return annotations


from datetime import datetime
