#!/usr/bin/env python3
"""
Shared test utilities for NEMESIS benchmarks
"""

import time
import json
import statistics
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import contextmanager


@contextmanager
def timed_operation(name: str):
    """Context manager to time operations"""
    print(f"  ⏱️  {name}...", end=" ", flush=True)
    start = time.perf_counter()
    yield
    duration = (time.perf_counter() - start) * 1000
    print(f"done ({duration:.1f}ms)")


class ResultCollector:
    """Collect and save test results"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.results = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
    
    def add_metric(self, name: str, value: Any, unit: str = ""):
        """Add a metric to results"""
        self.results["metrics"][name] = {
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat()
        }
    
    def save(self, output_dir: Optional[Path] = None) -> Path:
        """Save results to JSON file"""
        if output_dir is None:
            output_dir = Path("reports/scale_tests")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{self.test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        return filepath
    
    def print_summary(self):
        """Print summary of results"""
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.test_name}")
        print(f"{'='*60}")
        for name, metric in self.results["metrics"].items():
            print(f"  {name}: {metric['value']} {metric['unit']}")


def calculate_throughput(total_requests: int, duration_seconds: float) -> float:
    """Calculate requests per second"""
    return total_requests / duration_seconds if duration_seconds > 0 else 0


def calculate_percentile(values: List[float], percentile: float) -> float:
    """Calculate percentile of values"""
    if not values:
        return 0
    sorted_values = sorted(values)
    index = int(len(sorted_values) * percentile / 100)
    return sorted_values[min(index, len(sorted_values) - 1)]