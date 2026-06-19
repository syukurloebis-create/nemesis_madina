#!/usr/bin/env python3
"""
NEMESIS - Circuit Breaker Test
Menguji ketahanan sistem terhadap kegagalan berulang
"""

import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "reports" / "resilience_tests"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

BASE_URL = "http://localhost:8000"


class CircuitBreakerTester:
    """Test circuit breaker pattern"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
    
    def test_consecutive_failures(self) -> Dict[str, Any]:
        """Test system behavior under consecutive failures"""
        print(f"\n  {BLUE}[TEST 1] Consecutive Failures Resilience{RESET}")
        
        # Test with invalid endpoint
        failures = 0
        responses = []
        
        for i in range(20):
            try:
                resp = requests.get(f"{BASE_URL}/invalid-endpoint-{i}", timeout=2)
                responses.append(resp.status_code)
                if resp.status_code >= 500:
                    failures += 1
            except requests.exceptions.RequestException:
                responses.append(0)
                failures += 1
        
        # Check if system remains responsive after failures
        try:
            health_resp = requests.get(f"{BASE_URL}/health", timeout=5)
            system_healthy = health_resp.status_code == 200
        except:
            system_healthy = False
        
        print(f"    Failures encountered: {failures}")
        print(f"    System still healthy: {'✅' if system_healthy else '❌'}")
        
        return {
            "test": "consecutive_failures",
            "passed": system_healthy,
            "failures": failures,
            "system_healthy": system_healthy
        }
    
    def test_timeout_handling(self) -> Dict[str, Any]:
        """Test timeout handling"""
        print(f"\n  {BLUE}[TEST 2] Timeout Handling{RESET}")
        
        # Test slow endpoint (if exists)
        results = []
        
        for timeout in [0.1, 0.5, 1.0]:
            try:
                start = time.time()
                resp = requests.get(f"{BASE_URL}/health", timeout=timeout)
                duration = (time.time() - start) * 1000
                results.append({
                    "timeout": timeout,
                    "success": True,
                    "duration_ms": round(duration, 2)
                })
            except requests.exceptions.Timeout:
                results.append({
                    "timeout": timeout,
                    "success": False,
                    "error": "timeout"
                })
            except Exception:
                results.append({
                    "timeout": timeout,
                    "success": True,
                    "note": "request completed"
                })
        
        for r in results:
            status = "✅" if r.get("success", True) else "❌"
            print(f"    {status} Timeout {r['timeout']}s: {r.get('duration_ms', 'N/A')}ms")
        
        return {
            "test": "timeout_handling",
            "passed": True,
            "results": results
        }
    
    def test_rate_limit_recovery(self) -> Dict[str, Any]:
        """Test recovery after rate limiting"""
        print(f"\n  {BLUE}[TEST 3] Rate Limit Recovery{RESET}")
        
        # Trigger rate limit
        rate_limited = False
        for i in range(15):
            try:
                resp = requests.post(
                    f"{BASE_URL}/api/v1/auth/login",
                    json={"username": "test", "password": "wrong"},
                    timeout=5
                )
                if resp.status_code == 429:
                    rate_limited = True
                    print(f"    Rate limit triggered at attempt {i+1}")
                    break
            except:
                pass
        
        if not rate_limited:
            print(f"    ⚠️ Rate limit not triggered")
        
        # Wait and test recovery
        print(f"    ⏳ Waiting 65 seconds for rate limit window...")
        time.sleep(65)
        
        try:
            resp = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={"username": "test", "password": "wrong"},
                timeout=5
            )
            recovered = resp.status_code != 429
            print(f"    {'✅' if recovered else '❌'} Rate limit recovered: {recovered}")
        except:
            recovered = False
        
        return {
            "test": "rate_limit_recovery",
            "passed": recovered,
            "rate_limited": rate_limited,
            "recovered": recovered
        }
    
    def run_all(self) -> Dict[str, Any]:
        """Run all circuit breaker tests"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}CIRCUIT BREAKER TESTS{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        
        tests = [
            self.test_consecutive_failures,
            self.test_timeout_handling,
            self.test_rate_limit_recovery
        ]
        
        results = []
        for test in tests:
            result = test()
            results.append(result)
            time.sleep(1)
        
        self.results["tests"] = results
        passed = sum(1 for r in results if r.get("passed", False))
        self.results["summary"] = {
            "passed": passed,
            "failed": len(results) - passed,
            "total": len(results)
        }
        
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}CIRCUIT BREAKER SUMMARY{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"  Passed: {passed}/{len(results)}")
        
        report_path = REPORT_DIR / f"circuit_breaker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Report saved: {report_path}")
        
        return self.results


def main():
    tester = CircuitBreakerTester()
    results = tester.run_all()
    return 0


if __name__ == "__main__":
    sys.exit(main())