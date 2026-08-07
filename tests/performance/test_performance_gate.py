# scripts/tests/performance/test_performance_gate.py (Complete)
"""
Performance gate tests with warmup and percentile.
"""

import sys
import time
import pytest
import asyncio
import statistics
from typing import List, Dict, Any
from pathlib import Path

from metadata_inventory.phase2_runner import Phase2Runner
from metadata_inventory.phase3_runner import Phase3Runner

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
pytestmark = pytest.mark.metadata_inventory


class TestPerformanceGate:
    """Performance gate with warmup and percentile."""
    
    @pytest.fixture
    def performance_config(self):
        """Performance test configuration."""
        return {
            "iterations": 20,
            "warmup": 5,
            "targets": {
                "discovery_small": {"max_ms": 100, "p95_ms": 150},
                "discovery_medium": {"max_ms": 2000, "p95_ms": 2500},
                "verification_small": {"max_ms": 200, "p95_ms": 300},
                "verification_medium": {"max_ms": 5000, "p95_ms": 6000},
            }
        }
    
    def _run_benchmark(self, runner_fn, iterations: int, warmup: int) -> List[float]:
        """Run benchmark with warmup."""
        # Warmup
        for _ in range(warmup):
            runner_fn()
        
        # Actual runs
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            runner_fn()
            end = time.perf_counter()
            times.append(end - start)
        
        return times
    
    def test_discovery_small(self, performance_config):
        """Test discovery on small dataset."""
        def run_discovery():
            runner = Phase2Runner()
            asyncio.run(runner.run())
        
        times = self._run_benchmark(
            run_discovery,
            iterations=performance_config["iterations"],
            warmup=performance_config["warmup"]
        )
        
        avg = statistics.mean(times) * 1000  # Convert to ms
        p95 = statistics.quantiles(times, n=100)[94] * 1000  # 95th percentile
        
        target = performance_config["targets"]["discovery_small"]
        
        # Check average and p95
        assert avg < target["max_ms"], f"Average {avg}ms > {target['max_ms']}ms"
        assert p95 < target["p95_ms"], f"P95 {p95}ms > {target['p95_ms']}ms"
    
    def test_verification_small(self, performance_config):
        """Test verification on small dataset."""
        def run_verification():
            runner = Phase3Runner()
            asyncio.run(runner.run())
        
        times = self._run_benchmark(
            run_verification,
            iterations=performance_config["iterations"],
            warmup=performance_config["warmup"]
        )
        
        avg = statistics.mean(times) * 1000
        p95 = statistics.quantiles(times, n=100)[94] * 1000
        
        target = performance_config["targets"]["verification_small"]
        
        assert avg < target["max_ms"], f"Average {avg}ms > {target['max_ms']}ms"
        assert p95 < target["p95_ms"], f"P95 {p95}ms > {target['p95_ms']}ms"