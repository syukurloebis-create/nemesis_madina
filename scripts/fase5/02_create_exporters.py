#!/usr/bin/env python3
"""
NEMESIS FASE 5 - Create Metrics Exporters
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EXPORTERS_DIR = PROJECT_ROOT / "backend" / "telemetry" / "exporters"

def create_exporters_structure():
    """Create exporters directory structure"""
    print("\n[1/4] Creating exporters directory...")
    EXPORTERS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py
    init_content = '''"""
Metrics Exporters - Export metrics to various backends
"""

from backend.telemetry.exporters.prometheus import PrometheusExporter
from backend.telemetry.exporters.file import FileExporter

__all__ = ['PrometheusExporter', 'FileExporter']
'''
    (EXPORTERS_DIR / "__init__.py").write_text(init_content)
    print("  [OK] Created __init__.py")
    return True

def create_prometheus_exporter():
    """Create prometheus.py exporter"""
    print("\n[2/4] Creating Prometheus exporter...")
    
    content = '''"""
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
'''
    
    file_path = EXPORTERS_DIR / "prometheus.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_file_exporter():
    """Create file.py exporter"""
    print("\n[3/4] Creating File exporter...")
    
    content = '''"""
File Exporter - Export metrics to file
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from backend.telemetry.metrics import metrics_registry


class FileExporter:
    """Export metrics to JSON file"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("./metrics_exports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.registry = metrics_registry
    
    def export(self, filename: str = None) -> Path:
        """Export metrics to file"""
        if filename is None:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        file_path = self.output_dir / filename
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.registry.get_all_metrics(),
            "prometheus_format": self.registry.get_prometheus_format()
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return file_path
    
    def export_periodically(self, interval_seconds: int = 60):
        """Export metrics periodically (use with background task)"""
        import threading
        import time
        
        def export_loop():
            while True:
                time.sleep(interval_seconds)
                self.export()
        
        thread = threading.Thread(target=export_loop, daemon=True)
        thread.start()
        return thread
    
    def get_latest_export(self) -> Optional[Path]:
        """Get latest export file"""
        exports = sorted(self.output_dir.glob("metrics_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        return exports[0] if exports else None
    
    def get_export_history(self, limit: int = 10) -> list:
        """Get export history"""
        exports = sorted(self.output_dir.glob("metrics_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        return [
            {
                "file": str(p),
                "size": p.stat().st_size,
                "modified": datetime.fromtimestamp(p.stat().st_mtime).isoformat()
            }
            for p in exports[:limit]
        ]
'''
    
    file_path = EXPORTERS_DIR / "file.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_grafana_exporter():
    """Create grafana.py exporter (optional)"""
    print("\n[4/4] Creating Grafana exporter...")
    
    content = '''"""
Grafana Exporter - Format metrics for Grafana
"""

from typing import Dict, Any, List
from backend.telemetry.metrics import metrics_registry


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
        from backend.telemetry.alerts import alert_manager
        
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
'''
    
    file_path = EXPORTERS_DIR / "grafana.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def main():
    print("\n" + "="*60)
    print("FASE 5: CREATE EXPORTERS")
    print("="*60)
    
    create_exporters_structure()
    create_prometheus_exporter()
    create_file_exporter()
    create_grafana_exporter()
    
    print("\n" + "="*60)
    print("[OK] Exporters created")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())