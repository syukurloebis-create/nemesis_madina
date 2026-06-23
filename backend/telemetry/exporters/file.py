"""
File Exporter - Export metrics to file
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from telemetry.metrics import metrics_registry


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
