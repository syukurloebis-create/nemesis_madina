#!/usr/bin/env python3
"""
NEMESIS FASE 8 - Load Testing
"""

import sys
import asyncio
import aiohttp
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import statistics

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "reports" / "fase8"


class LoadTester:
    """Load testing for NEMESIS API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {}
        }
    
    async def test_endpoint(self, session: aiohttp.ClientSession, endpoint: str) -> float:
        """Test single endpoint and return latency"""
        start = time.perf_counter()
        try:
            async with session.get(f"{self.base_url}{endpoint}") as resp:
                await resp.text()
                return (time.perf_counter() - start) * 1000
        except:
            return -1
    
    async def run_concurrent_test(self, endpoint: str, concurrency: int, duration: int) -> Dict[str, Any]:
        """Run concurrent requests to an endpoint"""
        print(f"\n  Testing {endpoint} with {concurrency} concurrent users for {duration}s...")
        
        latencies = []
        errors = 0
        requests_completed = 0
        
        async def worker():
            nonlocal errors, requests_completed
            async with aiohttp.ClientSession() as session:
                end_time = time.perf_counter() + duration
                while time.perf_counter() < end_time:
                    latency = await self.test_endpoint(session, endpoint)
                    if latency > 0:
                        latencies.append(latency)
                        requests_completed += 1
                    else:
                        errors += 1
                    await asyncio.sleep(0.01)  # Small delay to prevent flooding
        
        # Run workers
        workers = [worker() for _ in range(concurrency)]
        await asyncio.gather(*workers)
        
        # Calculate statistics
        if latencies:
            avg_latency = statistics.mean(latencies)
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
            p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
        else:
            avg_latency = p95_latency = p99_latency = 0
        
        throughput = requests_completed / duration
        
        return {
            "endpoint": endpoint,
            "concurrency": concurrency,
            "duration": duration,
            "requests_completed": requests_completed,
            "errors": errors,
            "throughput": round(throughput, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": round(p95_latency, 2),
            "p99_latency_ms": round(p99_latency, 2)
        }
    
    async def run_all_tests(self):
        """Run all load tests"""
        print("\n" + "="*60)
        print("LOAD TESTING")
        print("="*60)
        
        endpoints = [
            "/health",
            "/metrics",
            "/api/v1/health"
        ]
        
        concurrency_levels = [10, 50, 100]
        duration = 10  # seconds per test
        
        all_results = []
        
        for endpoint in endpoints:
            for concurrency in concurrency_levels:
                result = await self.run_concurrent_test(endpoint, concurrency, duration)
                all_results.append(result)
                
                # Print result
                status = "✅" if result["errors"] == 0 else "⚠️"
                print(f"    {status} {endpoint} (c={concurrency}): "
                      f"{result['throughput']:.0f} req/s, "
                      f"avg={result['avg_latency_ms']:.1f}ms, "
                      f"p95={result['p95_latency_ms']:.1f}ms")
        
        self.results["tests"] = all_results
        
        # Calculate summary
        avg_throughput = statistics.mean([r["throughput"] for r in all_results])
        avg_latency = statistics.mean([r["avg_latency_ms"] for r in all_results])
        total_errors = sum([r["errors"] for r in all_results])
        
        self.results["summary"] = {
            "total_tests": len(all_results),
            "avg_throughput": round(avg_throughput, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "total_errors": total_errors,
            "passed": total_errors == 0
        }
        
        # Save report
        report_path = REPORT_DIR / "load_test_results.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Load test report saved: {report_path}")
        
        return self.results


async def main():
    tester = LoadTester()
    results = await tester.run_all_tests()
    
    print("\n" + "="*60)
    print("LOAD TEST SUMMARY")
    print("="*60)
    print(f"  Average Throughput: {results['summary']['avg_throughput']} req/s")
    print(f"  Average Latency: {results['summary']['avg_latency_ms']} ms")
    print(f"  Total Errors: {results['summary']['total_errors']}")
    
    if results['summary']['passed']:
        print("\n✅ Load tests passed!")
        return 0
    else:
        print("\n⚠️ Load tests had errors")
        return 1


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success == 0 else 1)