"""
Test untuk mensimulasikan error scenarios
Mengidentifikasi bagaimana sistem merespon kegagalan
"""

import requests
import json
import time

def test_invalid_requests():
    """Test API response to invalid requests"""
    print("\n🔍 TEST: Invalid Request Handling")
    print("=" * 60)
    
    test_cases = [
        ("POST /cases with empty body", 
         "POST", "/cases", {}),
        ("POST /cases with missing title", 
         "POST", "/cases", {"description": "No title"}),
        ("GET /cases/invalid-id", 
         "GET", "/cases/not-a-valid-uuid", None),
        ("POST /cases with malformed JSON", 
         "POST", "/cases", "not json"),
    ]
    
    for name, method, endpoint, data in test_cases:
        try:
            if method == "POST":
                if data == "not json":
                    resp = requests.post(f"http://localhost{endpoint}", 
                                       data="not json", 
                                       headers={"Content-Type": "application/json"})
                else:
                    resp = requests.post(f"http://localhost{endpoint}", json=data)
            else:
                resp = requests.get(f"http://localhost{endpoint}")
            
            print(f"\n📝 {name}:")
            print(f"   Status: {resp.status_code}")
            if resp.status_code >= 400:
                print(f"   Response: {resp.text[:100]}")
                
        except Exception as e:
            print(f"\n❌ {name}: Exception - {str(e)[:100]}")

def test_database_failure_simulation():
    """Test system behavior when database is unavailable"""
    print("\n🔍 TEST: Database Failure Simulation")
    print("=" * 60)
    
    # Note: This is a simulation - don't actually disconnect in production
    print("⚠️ This is a simulation. In production, test with controlled environment.")
    
    # Check health endpoint reports database status
    resp = requests.get("http://localhost/health")
    data = resp.json()
    
    print(f"\n📊 Health endpoint reports:")
    print(f"   Status: {data.get('status')}")
    print(f"   Database connected: {data.get('database') == 'connected'}")

def test_timeout_scenario():
    """Test API timeout handling"""
    print("\n🔍 TEST: Timeout Handling")
    print("=" * 60)
    
    # Test with very short timeout
    try:
        resp = requests.get("http://localhost/cases", timeout=0.001)
        print("❌ Request should have timed out but didn't")
    except requests.exceptions.Timeout:
        print("✅ Request properly timed out")
    except Exception as e:
        print(f"⚠️ Unexpected error: {type(e).__name__}")

if __name__ == "__main__":
    test_invalid_requests()
    test_database_failure_simulation()
    test_timeout_scenario()