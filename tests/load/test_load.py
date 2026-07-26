"""
Load Testing Script for NEMESIS V8.1
"""
import asyncio
import aiohttp
import time
import json

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import statistics


@dataclass
class LoadTestResult:
    """Load test result"""
    endpoint: str
    total_requests: int
    success_count: int
    error_count: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "endpoint": self.endpoint,
            "total_requests": self.total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "avg_response_time": self.avg_response_time,
            "min_response_time": self.min_response_time,
            "max_response_time": self.max_response_time,
            "p95_response_time": self.p95_response_time,
            "p99_response_time": self.p99_response_time,
            "requests_per_second": self.requests_per_second
        }


class LoadTester:
    """
    Load Testing Engine
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[LoadTestResult] = []

    async def test_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        payload: Optional[Dict[str, Any]] = None,
        concurrency: int = 10,
        total_requests: int = 100
    ) -> LoadTestResult:
        """Test a single endpoint under load"""
        start_time = time.time()
        response_times = []
        success_count = 0
        error_count = 0

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrency)

        async def make_request(session, request_id: int):
            nonlocal success_count, error_count
            async with semaphore:
                try:
                    request_start = time.time()

                    if method == "GET":
                        async with session.get(f"{self.base_url}{endpoint}") as response:
                            response_time = (time.time() - request_start) * 1000
                            response_times.append(response_time)
                            if response.status < 400:
                                success_count += 1
                            else:
                                error_count += 1
                    elif method == "POST":
                        async with session.post(
                            f"{self.base_url}{endpoint}",
                            json=payload or {}
                        ) as response:
                            response_time = (time.time() - request_start) * 1000
                            response_times.append(response_time)
                            if response.status < 400:
                                success_count += 1
                            else:
                                error_count += 1
                except Exception as e:
                    error_count += 1
                    response_times.append(0)

        async with aiohttp.ClientSession() as session:
            tasks = [
                make_request(session, i)
                for i in range(total_requests)
            ]
            await asyncio.gather(*tasks)

        total_time = time.time() - start_time

        # Calculate statistics
        avg_time = statistics.mean(response_times) if response_times else 0
        min_time = min(response_times) if response_times else 0
        max_time = max(response_times) if response_times else 0

        sorted_times = sorted(response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)
        p95_time = sorted_times[p95_index] if sorted_times else 0
        p99_time = sorted_times[p99_index] if sorted_times else 0

        return LoadTestResult(
            endpoint=endpoint,
            total_requests=total_requests,
            success_count=success_count,
            error_count=error_count,
            avg_response_time=avg_time,
            min_response_time=min_time,
            max_response_time=max_time,
            p95_response_time=p95_time,
            p99_response_time=p99_time,
            requests_per_second=total_requests / total_time if total_time > 0 else 0
        )

    async def run_load_test(
        self,
        endpoints: List[Dict[str, Any]],
        concurrency: int = 10,
        total_requests: int = 100
    ) -> List[LoadTestResult]:
        """Run load test on multiple endpoints"""
        self.results = []

        for endpoint_config in endpoints:
            result = await self.test_endpoint(
                endpoint=endpoint_config["path"],
                method=endpoint_config.get("method", "GET"),
                payload=endpoint_config.get("payload"),
                concurrency=concurrency,
                total_requests=total_requests
            )
            self.results.append(result)
            print(f"✅ {endpoint_config['path']}: {result.success_count}/{result.total_requests} success, avg: {result.avg_response_time:.2f}ms")

        return self.results

    def generate_report(self) -> Dict[str, Any]:
        """Generate load test report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "results": [r.to_dict() for r in self.results],
            "summary": {
                "total_endpoints": len(self.results),
                "total_requests": sum(r.total_requests for r in self.results),
                "total_success": sum(r.success_count for r in self.results),
                "total_errors": sum(r.error_count for r in self.results),
                "overall_success_rate": (
                    sum(r.success_count for r in self.results) /
                    sum(r.total_requests for r in self.results) * 100
                ) if self.results else 0,
                "overall_avg_response": statistics.mean(
                    [r.avg_response_time for r in self.results]
                ) if self.results else 0
            }
        }


# Run load test
async def main():
    tester = LoadTester()

    endpoints = [
        {"path": "/health", "method": "GET"},
        {"path": "/api/v1/cases/stats", "method": "GET"},
        {"path": "/api/v1/fraud/stats", "method": "GET"},
        {"path": "/api/v1/graph/metrics", "method": "GET"},
    ]

    print("🚀 Starting load test...")
    print("=" * 40)

    results = await tester.run_load_test(
        endpoints=endpoints,
        concurrency=20,
        total_requests=200
    )

    report = tester.generate_report()
    print("\n📊 Load Test Report:")
    print("=" * 40)
    print(f"Total Requests: {report['summary']['total_requests']}")
    print(f"Success Rate: {report['summary']['overall_success_rate']:.2f}%")
    print(f"Average Response: {report['summary']['overall_avg_response']:.2f}ms")

    for result in results:
        print(f"\n  {result.endpoint}:")
        print(f"    Avg: {result.avg_response_time:.2f}ms")
        print(f"    P95: {result.p95_response_time:.2f}ms")
        print(f"    P99: {result.p99_response_time:.2f}ms")
        print(f"    RPS: {result.requests_per_second:.2f}")

    return report

if __name__ == "__main__":
    report = asyncio.run(main())
    with open("load_test_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)