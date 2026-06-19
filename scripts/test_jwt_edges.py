#!/usr/bin/env python3
"""
NEMESIS - JWT Edge Cases Test
"""

import sys
import time
import json
import jwt
import requests
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "reports" / "security_tests"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

BASE_URL = "http://localhost:8000"
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"


def utc_now():
    """Get UTC datetime (Python 3.12 compatible)"""
    return datetime.now(timezone.utc)


class JWTEdgeTester:
    def __init__(self):
        self.results = {"timestamp": datetime.now().isoformat(), "tests": []}
    
    def create_token(self, user_id: str, username: str, role: str, expires_in_seconds: int = 3600) -> str:
        now = utc_now()
        expire = now + timedelta(seconds=expires_in_seconds)
        payload = {
            "sub": user_id,
            "username": username,
            "role": role,
            "type": "access",
            "exp": expire,
            "iat": now
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    def test_valid_token(self):
        print(f"\n  {BLUE}[TEST 1] Valid Token{RESET}")
        token = self.create_token("user_001", "testuser", "viewer")
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            resp = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers, timeout=5)
            if resp.status_code == 200:
                print(f"    ✅ Valid token accepted")
                return {"test": "valid_token", "passed": True}
            else:
                print(f"    ❌ Valid token rejected (HTTP {resp.status_code})")
                return {"test": "valid_token", "passed": False}
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return {"test": "valid_token", "passed": False}
    
    def test_expired_token(self):
        print(f"\n  {BLUE}[TEST 2] Expired Token{RESET}")
        token = self.create_token("user_001", "testuser", "viewer", expires_in_seconds=1)
        time.sleep(2)
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            resp = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers, timeout=5)
            if resp.status_code == 401:
                print(f"    ✅ Expired token rejected")
                return {"test": "expired_token", "passed": True}
            else:
                print(f"    ❌ Expired token accepted (HTTP {resp.status_code})")
                return {"test": "expired_token", "passed": False}
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return {"test": "expired_token", "passed": False}
    
    def test_malformed_token(self):
        print(f"\n  {BLUE}[TEST 3] Malformed Token{RESET}")
        malformed = ["invalid.token.here", "abc123", "Bearer "]
        results = []
        
        for token in malformed:
            headers = {"Authorization": f"Bearer {token}" if token else ""}
            resp = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers, timeout=5)
            is_rejected = resp.status_code == 401
            results.append(is_rejected)
            print(f"    {'✅' if is_rejected else '❌'} Token: '{token[:20]}' -> {resp.status_code}")
        
        passed = all(results)
        return {"test": "malformed_token", "passed": passed}
    
    def test_tampered_token(self):
        print(f"\n  {BLUE}[TEST 4] Tampered Token{RESET}")
        valid_token = self.create_token("user_001", "testuser", "viewer")
        parts = valid_token.split('.')
        tampered = f"{parts[0]}.{parts[1]}.tampered" if len(parts) == 3 else valid_token + ".x"
        headers = {"Authorization": f"Bearer {tampered}"}
        
        resp = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers, timeout=5)
        if resp.status_code == 401:
            print(f"    ✅ Tampered token rejected")
            return {"test": "tampered_token", "passed": True}
        else:
            print(f"    ❌ Tampered token accepted (HTTP {resp.status_code})")
            return {"test": "tampered_token", "passed": False}
    
    def run_all(self):
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}JWT EDGE CASES TEST{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        
        results = [
            self.test_valid_token(),
            self.test_expired_token(),
            self.test_malformed_token(),
            self.test_tampered_token()
        ]
        
        self.results["tests"] = results
        passed = sum(1 for r in results if r.get("passed", False))
        
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"  Passed: {passed}/{len(results)}")
        
        report_path = REPORT_DIR / f"jwt_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Report saved: {report_path}")
        return self.results


def main():
    tester = JWTEdgeTester()
    tester.run_all()
    return 0


if __name__ == "__main__":
    sys.exit(main())
