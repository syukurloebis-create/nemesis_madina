#!/usr/bin/env python3
"""
NEMESIS - Memory Usage Monitor
Monitor memory usage during tests
"""

import sys
import time
import json
import psutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
REPORT_DIR = PROJECT_ROOT / "reports" / "scale_tests"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


class MemoryMonitor:
    """Monitor memory usage over time"""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.samples: List[Dict] = []
        self.running = False
        self.process = psutil.Process()
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        memory_info = self.process.memory_info()
        
        return {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": self.process.memory_percent(),
            "cpu_percent": self.process.cpu_percent(interval=0.1)
        }
    
    def start(self, duration: float = None):
        """Start monitoring"""
        self.running = True
        start_time = time.time()
        
        print(f"\n🔍 Monitoring memory usage (interval: {self.interval}s)...")
        
        while self.running:
            self.samples.append(self.get_current_stats())
            
            # Check duration
            if duration and (time.time() - start_time) >= duration:
                break
            
            time.sleep(self.interval)
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
    
    def get_report(self) -> Dict[str, Any]:
        """Generate monitoring report"""
        if not self.samples:
            return {"error": "No samples collected"}
        
        rss_values = [s["rss_mb"] for s in self.samples]
        
        return {
            "duration_seconds": self.samples[-1]["timestamp"] - self.samples[0]["timestamp"],
            "sample_count": len(self.samples),
            "min_rss_mb": round(min(rss_values), 1),
            "max_rss_mb": round(max(rss_values), 1),
            "avg_rss_mb": round(sum(rss_values) / len(rss_values), 1),
            "final_rss_mb": round(rss_values[-1], 1),
            "memory_increase_mb": round(rss_values[-1] - rss_values[0], 1) if len(rss_values) > 1 else 0,
            "samples": self.samples
        }
    
    def save_report(self, name: str = "memory_monitor"):
        """Save report to file"""
        report = self.get_report()
        report_path = REPORT_DIR / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Memory report saved: {report_path}")
        return report_path


def monitor_background(duration: int = 60, interval: float = 1.0):
    """Run memory monitor in background"""
    monitor = MemoryMonitor(interval)
    
    print(f"📊 Monitoring memory for {duration} seconds...")
    monitor.start(duration)
    
    report = monitor.get_report()
    
    print(f"\n{'='*60}")
    print(f"MEMORY MONITOR REPORT")
    print(f"{'='*60}")
    print(f"  Duration:        {report['duration_seconds']:.1f}s")
    print(f"  Min RSS:         {report['min_rss_mb']:.1f} MB")
    print(f"  Max RSS:         {report['max_rss_mb']:.1f} MB")
    print(f"  Avg RSS:         {report['avg_rss_mb']:.1f} MB")
    print(f"  Final RSS:       {report['final_rss_mb']:.1f} MB")
    print(f"  Memory increase: {report['memory_increase_mb']:.1f} MB")
    
    monitor.save_report()


def main():
    parser = argparse.ArgumentParser(description="NEMESIS Memory Monitor")
    parser.add_argument("--duration", type=int, default=60, help="Monitoring duration in seconds")
    parser.add_argument("--interval", type=float, default=1.0, help="Sampling interval in seconds")
    
    args = parser.parse_args()
    
    monitor_background(args.duration, args.interval)


if __name__ == "__main__":
    main()