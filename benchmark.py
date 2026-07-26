import time
import requests
import concurrent.futures
from statistics import mean, min, max

def test_endpoint(url):
    start = time.time()
    try:
        response = requests.get(url, timeout=5)
        elapsed = (time.time() - start) * 1000
        return {'url': url, 'status': response.status_code, 'time': elapsed}
    except Exception as e:
        return {'url': url, 'status': 'error', 'time': 0}

urls = [
    'http://localhost:8000/health',
    'http://localhost:8000/api/v1/cases/stats',
    'http://localhost:8000/api/v1/alerts/stats',
    'http://localhost:8000/api/v1/fraud/stats',
    'http://localhost:8000/api/v1/graph/metrics',
]

print("Running benchmark...")
print("=" * 60)

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(test_endpoint, url) for url in urls]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

for result in results:
    if result['status'] == 200:
        print(f"✅ {result['url']}: {result['time']:.2f}ms")
    else:
        print(f"❌ {result['url']}: {result['status']}")

times = [r['time'] for r in results if r['status'] == 200]
if times:
    print(f"\n📊 Summary:")
    print(f"  Average: {mean(times):.2f}ms")
    print(f"  Min: {min(times):.2f}ms")
    print(f"  Max: {max(times):.2f}ms")
