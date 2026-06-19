"""
Performance test untuk load balancer distribution
Mengukur efektivitas load balancing
"""

import requests
import time
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_load_distribution():
    """Test load balancer distribution across instances"""
    print("\n🔍 TEST: Load Balancer Distribution")
    print("=" * 60)
    
    url = "http://localhost/health"
    requests_count = 100
    
    print(f"📊 Sending {requests_count} requests...")
    
    responses = []
    start_time = time.time()
    
    for i in range(requests_count):
        try:
            resp = requests.get(url, timeout=5)
            responses.append(resp.status_code)
        except Exception as e:
            responses.append(0)
    
    elapsed = time.time() - start_time
    
    status_counts = Counter(responses)
    
    print(f"\n📈 Results:")
    print(f"   Total requests: {requests_count}")
    print(f"   Time taken: {elapsed:.2f}s")
    print(f"   Requests/sec: {requests_count/elapsed:.1f}")
    print(f"   Success rate: {status_counts.get(200, 0)}/{requests_count} ({status_counts.get(200, 0)/requests_count*100:.1f}%)")
    
    if status_counts.get(503, 0) > 0:
        print(f"   ⚠️ Unhealthy responses: {status_counts.get(503, 0)}")

def test_concurrent_requests():
    """Test concurrent request handling"""
    print("\n🔍 TEST: Concurrent Request Handling")
    print("=" * 60)
    
    url = "http://localhost/cases"
    concurrent = 20
    total = 100
    
    print(f"📊 Sending {total} concurrent requests (batch of {concurrent})...")
    
    def make_request():
        try:
            resp = requests.post(
                url,
                json={"title": f"Load Test Case", "description": "Concurrent test"},
                timeout=10
            )
            return resp.status_code
        except Exception as e:
            return 0
    
    start_time = time.time()
    all_responses = []
    
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = [executor.submit(make_request) for _ in range(total)]
        for future in as_completed(futures):
            all_responses.append(future.result())
    
    elapsed = time.time() - start_time
    
    success_count = sum(1 for r in all_responses if r == 200)
    error_count = sum(1 for r in all_responses if r == 0)
    other_count = len(all_responses) - success_count - error_count
    
    print(f"\n📈 Results:")
    print(f"   Total requests: {total}")
    print(f"   Concurrent workers: {concurrent}")
    print(f"   Time taken: {elapsed:.2f}s")
    print(f"   Success: {success_count} ({success_count/total*100:.1f}%)")
    print(f"   Errors: {error_count} ({error_count/total*100:.1f}%)")
    print(f"   Other: {other_count}")
    print(f"   Throughput: {total/elapsed:.1f} req/s")

def test_response_time():
    """Test response time distribution"""
    print("\n🔍 TEST: Response Time Distribution")
    print("=" * 60)
    
    url = "http://localhost/cases"
    requests_count = 50
    
    print(f"📊 Measuring response times for {requests_count} requests...")
    
    response_times = []
    
    for i in range(requests_count):
        start = time.time()
        try:
            resp = requests.post(
                url,
                json={"title": f"RT Test {i}", "description": "Response time test"},
                timeout=10
            )
            elapsed = (time.time() - start) * 1000  # milliseconds
            response_times.append((resp.status_code, elapsed))
        except Exception as e:
            response_times.append((0, 0))
    
    successful_times = [t for code, t in response_times if code == 200]
    
    if successful_times:
        print(f"\n📈 Results (successful requests only):")
        print(f"   Min: {min(successful_times):.1f}ms")
        print(f"   Max: {max(successful_times):.1f}ms")
        print(f"   Avg: {sum(successful_times)/len(successful_times):.1f}ms")
        
        # Percentiles
        sorted_times = sorted(successful_times)
        p50 = sorted_times[len(sorted_times)//2]
        p95 = sorted_times[int(len(sorted_times)*0.95)]
        p99 = sorted_times[int(len(sorted_times)*0.99)]
        
        print(f"   P50: {p50:.1f}ms")
        print(f"   P95: {p95:.1f}ms")
        print(f"   P99: {p99:.1f}ms")

if __name__ == "__main__":
    test_load_distribution()
    test_concurrent_requests()
    test_response_time()