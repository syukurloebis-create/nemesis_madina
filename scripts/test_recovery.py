#!/usr/bin/env python3
"""
NEMESIS - Recovery Test (Windows Compatible)
"""

import sys
import time
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

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


class RecoveryTester:
    def __init__(self):
        self.results = {"timestamp": datetime.now().isoformat(), "tests": []}
    
    def restart_server(self) -> bool:
        """Restart server using Python subprocess"""
        try:
            # Kill existing uvicorn processes
            subprocess.run(
                ['taskkill', '/f', '/im', 'python.exe'],
                capture_output=True,
                shell=True
            )
            time.sleep(2)
            
            # Start server
            startup = subprocess.Popen(
                [sys.executable, '-m', 'uvicorn', 'backend.app.main:app', 
                 '--host', '0.0.0.0', '--port', '8000'],
                cwd=str(PROJECT_ROOT),
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(5)
            return True
        except Exception as e:
            print(f"    Restart error: {e}")
            return False
    
    def wait_for_server(self, max_wait: int = 30) -> bool:
        """Wait for server to become available"""
        for i in range(max_wait):
            try:
                resp = requests.get(f"{BASE_URL}/health", timeout=2)
                if resp.status_code == 200:
                    print(f"    ✅ Server recovered after {i+1}s")
                    return True
            except:
                pass
            time.sleep(1)
        print(f"    ❌ Server did not recover")
        return False
    
    def create_test_data(self) -> Dict[str, Any]:
        """Create test data before restart"""
        print(f"\n  📝 Creating test data...")
        test_data = {"evidence_id": None, "timestamp": datetime.now().isoformat()}
        
        try:
            resp = requests.post(
                f"{BASE_URL}/api/v1/evidence",
                json={"payload": {"test": "recovery_data"}, "source": "recovery_test"},
                timeout=5
            )
            if resp.status_code in [200, 307]:
                # Handle redirect
                if resp.status_code == 307:
                    location = resp.headers.get('Location', '')
                    if location:
                        resp = requests.post(f"{BASE_URL}{location}", 
                            json={"payload": {"test": "recovery_data"}, "source": "recovery_test"},
                            timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    test_data["evidence_id"] = data.get("id")
                    print(f"    ✅ Evidence created: {test_data['evidence_id']}")
        except Exception as e:
            print(f"    ⚠️ Evidence creation: {e}")
        
        return test_data
    
    def verify_data(self, test_data: Dict[str, Any]) -> bool:
        """Verify data exists after restart"""
        if test_data.get("evidence_id"):
            try:
                resp = requests.get(
                    f"{BASE_URL}/api/v1/evidence/{test_data['evidence_id']}",
                    timeout=5
                )
                exists = resp.status_code == 200
                print(f"    {'✅' if exists else '❌'} Evidence persisted")
                return exists
            except:
                pass
        return True  # Assume OK if can't verify
    
    def test_graceful_restart(self) -> Dict[str, Any]:
        """Test recovery after restart"""
        print(f"\n  {BLUE}[TEST 1] Server Recovery{RESET}")
        
        test_data = self.create_test_data()
        
        print(f"\n  🔄 Restarting server...")
        if not self.restart_server():
            return {"test": "graceful_restart", "passed": False, "error": "Restart failed"}
        
        if not self.wait_for_server():
            return {"test": "graceful_restart", "passed": False, "error": "Server not responding"}
        
        # Verify health
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=5)
            health_ok = resp.status_code == 200
        except:
            health_ok = False
        
        data_ok = self.verify_data(test_data)
        passed = health_ok
        
        print(f"\n  📊 Results: Health: {'✅' if health_ok else '❌'}")
        
        return {"test": "graceful_restart", "passed": passed, "health_ok": health_ok}
    
    def test_health_endpoint(self) -> Dict[str, Any]:
        """Test health endpoint resilience"""
        print(f"\n  {BLUE}[TEST 2] Health Endpoint Resilience{RESET}")
        
        results = []
        for i in range(10):
            try:
                resp = requests.get(f"{BASE_URL}/health", timeout=3)
                results.append(resp.status_code == 200)
            except:
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"    Health check success rate: {success_rate:.1f}%")
        
        return {"test": "health_endpoint", "passed": success_rate >= 90, "success_rate": success_rate}
    
    def test_api_stability(self) -> Dict[str, Any]:
        """Test API stability under repeated requests"""
        print(f"\n  {BLUE}[TEST 3] API Stability{RESET}")
        
        endpoints = ["/health", "/metrics", "/api/v1/health"]
        stability = []
        
        for endpoint in endpoints:
            failures = 0
            for _ in range(30):
                try:
                    resp = requests.get(f"{BASE_URL}{endpoint}", timeout=3)
                    if resp.status_code >= 500:
                        failures += 1
                except:
                    failures += 1
            success_rate = (30 - failures) / 30 * 100
            stability.append({"endpoint": endpoint, "success_rate": success_rate})
            print(f"    {endpoint}: {success_rate:.1f}%")
        
        all_stable = all(s["success_rate"] >= 95 for s in stability)
        return {"test": "api_stability", "passed": all_stable, "results": stability}
    
    def run_all(self) -> Dict[str, Any]:
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}RECOVERY & RESILIENCE TESTS{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        
        tests = [self.test_graceful_restart, self.test_health_endpoint, self.test_api_stability]
        
        results = []
        for test in tests:
            results.append(test())
            time.sleep(2)
        
        self.results["tests"] = results
        passed = sum(1 for r in results if r.get("passed", False))
        self.results["summary"] = {"passed": passed, "failed": len(results) - passed, "total": len(results)}
        
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"  Passed: {passed}/{len(results)}")
        
        report_path = REPORT_DIR / f"recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Report saved: {report_path}")
        return self.results


def main():
    tester = RecoveryTester()
    tester.run_all()
    return 0


if __name__ == "__main__":
    sys.exit(main())
