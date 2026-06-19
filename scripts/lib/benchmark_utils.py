#!/usr/bin/env python3
"""
Benchmark utilities for NEMESIS
"""

import time
import json
import statistics
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed


def measure_latency(url: str, iterations: int = 10) -> Dict[str, Any]:
    """Measure endpoint latency"""
    import requests
    
    latencies = []
    errors = 0
    
    for _ in range(iterations):
        try:
            start = time.perf_counter()
            resp = requests.get(url, timeout=5)
            duration = (time.perf_counter() - start) * 1000
            latencies.append(duration)
        except Exception:
            errors += 1
    
    if latencies:
        return {
            "url": url,
            "iterations": iterations,
            "avg_ms": round(statistics.mean(latencies), 2),
            "min_ms": round(min(latencies), 2),
            "max_ms": round(max(latencies), 2),
            "p95_ms": round(statistics.quantiles(latencies, n=20)[18], 2) if len(latencies) >= 20 else round(max(latencies), 2),
            "errors": errors,
            "success_rate": round((iterations - errors) / iterations * 100, 2)
        }
    
    return {
        "url": url,
        "error": "All requests failed",
        "errors": errors
    }


def concurrent_test(url: str, concurrency: int = 50) -> Dict[str, Any]:
    """Run concurrent requests test"""
    import requests
    
    def make_request():
        try:
            start = time.perf_counter()
            resp = requests.get(url, timeout=10)
            duration = (time.perf_counter() - start) * 1000
            return {"success": True, "duration": duration, "status": resp.status_code}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    start_time = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(make_request) for _ in range(concurrency)]
        results = [f.result() for f in as_completed(futures)]
    
    duration = (time.perf_counter() - start_time) * 1000
    
    successes = [r for r in results if r["success"]]
    errors = [r for r in results if not r["success"]]
    
    latencies = [r["duration"] for r in successes]
    
    return {
        "url": url,
        "concurrency": concurrency,
        "total": concurrency,
        "success": len(successes),
        "errors": len(errors),
        "duration_ms": round(duration, 2),
        "avg_latency_ms": round(statistics.mean(latencies), 2) if latencies else 0,
        "throughput": round(len(successes) / (duration / 1000), 2)
    }


if __name__ == "__main__":
    # Quick test
    result = measure_latency("http://localhost:8000/health", 5)
    print(json.dumps(result, indent=2))