#!/usr/bin/env python3
"""
NEMESIS V8+ - Dashboard Endpoint Testing Script
Testing semua endpoint yang digunakan oleh dashboard frontend
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BASE_URL = "http://localhost"  # Load balancer (port 80)
# BASE_URL = "http://localhost:8000"  # Direct API (uncomment if needed)

# Test credentials
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class DashboardTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token = None
        self.user = None
        self.test_case_id = None
        self.test_evidence_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "details": []
        }
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "ERROR":
            print(f"[{timestamp}] {RED}❌ {message}{RESET}")
        elif level == "SUCCESS":
            print(f"[{timestamp}] {GREEN}✅ {message}{RESET}")
        elif level == "WARNING":
            print(f"[{timestamp}] {YELLOW}⚠️ {message}{RESET}")
        elif level == "INFO":
            print(f"[{timestamp}] {BLUE}📌 {message}{RESET}")
        else:
            print(f"[{timestamp}] {message}")
    
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        self.results["total"] += 1
        if passed:
            self.results["passed"] += 1
            self.log(f"{test_name}: PASSED", "SUCCESS")
        else:
            self.results["failed"] += 1
            self.log(f"{test_name}: FAILED - {details}", "ERROR")
        self.results["details"].append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    def request(self, method: str, endpoint: str, data: Dict = None, files: Dict = None) -> Optional[Dict]:
        """Make HTTP request with authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                if files:
                    # For file upload, remove Content-Type header (requests will set multipart)
                    headers.pop("Content-Type", None)
                    response = requests.post(url, headers=headers, files=files, timeout=30)
                else:
                    response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            else:
                return None
            
            if response.status_code in [200, 201]:
                return response.json() if response.text else {"status": "success"}
            else:
                self.log(f"Request failed: {response.status_code} - {response.text}", "ERROR")
                return None
        except requests.exceptions.ConnectionError:
            self.log(f"Connection error to {url}", "ERROR")
            return None
        except Exception as e:
            self.log(f"Request error: {e}", "ERROR")
            return None
    
    # =========================================================
    # AUTHENTICATION TESTS
    # =========================================================
    
    def test_login(self) -> bool:
        self.log("Testing authentication...", "INFO")
        
        response = self.request("POST", "/auth/login", data=TEST_USER)
        if response and "access_token" in response:
            self.token = response["access_token"]
            self.user = response.get("user")
            self.log(f"Login successful as {self.user.get('username')}", "SUCCESS")
            return True
        
        self.log("Login failed", "ERROR")
        return False
    
    def test_health(self) -> bool:
        response = self.request("GET", "/health")
        passed = response and response.get("status") == "healthy"
        self.log_result("Health Check", passed, "Status not healthy" if not passed else "")
        return passed
    
    def test_root(self) -> bool:
        response = self.request("GET", "/")
        passed = response and "service" in response
        self.log_result("Root Endpoint", passed, "Service not found" if not passed else "")
        return passed
    
    # =========================================================
    # DASHBOARD TESTS
    # =========================================================
    
    def test_dashboard_summary(self) -> bool:
        response = self.request("GET", "/api/dashboard/summary")
        passed = response and "total_cases" in response
        self.log_result("Dashboard Summary", passed, "Missing total_cases" if not passed else "")
        if passed:
            self.log(f"   Total cases: {response.get('total_cases', 0)}", "INFO")
        return passed
    
    def test_integrity_summary(self) -> bool:
        response = self.request("GET", "/integrity/summary/overview")
        passed = response and "integrity_score" in response
        self.log_result("Integrity Summary", passed, "Missing integrity_score" if not passed else "")
        if passed:
            self.log(f"   Integrity score: {response.get('integrity_score', 0)}%", "INFO")
        return passed
    
    def test_findings_summary(self) -> bool:
        response = self.request("GET", "/findings/dashboard/summary")
        passed = response and "total_findings" in response
        self.log_result("Findings Dashboard", passed, "Missing total_findings" if not passed else "")
        if passed:
            self.log(f"   Total findings: {response.get('total_findings', 0)}", "INFO")
        return passed
    
    # =========================================================
    # CASE MANAGEMENT TESTS
    # =========================================================
    
    def test_create_case(self) -> bool:
        data = {
            "title": "Automated Test Case",
            "description": f"Created by test script at {datetime.now().isoformat()}",
            "priority": "HIGH"
        }
        response = self.request("POST", "/cases/", data=data)
        passed = response and "id" in response and "event_hash" in response
        if passed:
            self.test_case_id = response["id"]
            self.log(f"   Case ID: {self.test_case_id}", "INFO")
            self.log(f"   Event hash: {response.get('event_hash', '')[:32]}...", "INFO")
        self.log_result("Create Case", passed, "Failed to create case" if not passed else "")
        return passed
    
    def test_get_cases(self) -> bool:
        response = self.request("GET", "/cases/")
        passed = response and isinstance(response, (dict, list))
        self.log_result("Get Cases List", passed, "Invalid response" if not passed else "")
        return passed
    
    def test_get_case(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping get_case - no case ID", "WARNING")
            return False
        response = self.request("GET", f"/cases/{self.test_case_id}")
        passed = response and response.get("id") == self.test_case_id
        self.log_result("Get Case Detail", passed, "Case not found" if not passed else "")
        return passed
    
    def test_update_case_status(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping update_status - no case ID", "WARNING")
            return False
        response = self.request("PUT", f"/cases/{self.test_case_id}/status", data={"status": "INVESTIGATING"})
        passed = response and "event_hash" in response
        self.log_result("Update Case Status", passed, "Failed to update status" if not passed else "")
        return passed
    
    def test_assign_case(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping assign_case - no case ID", "WARNING")
            return False
        response = self.request("PUT", f"/cases/{self.test_case_id}/assign", data={"assigned_to": "investigator_01"})
        passed = response and "event_version" in response
        self.log_result("Assign Case", passed, "Failed to assign" if not passed else "")
        return passed
    
    # =========================================================
    # EVENT & REPLAY TESTS
    # =========================================================
    
    def test_replay_timeline(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping replay_timeline - no case ID", "WARNING")
            return False
        response = self.request("GET", f"/replay/case/{self.test_case_id}/timeline?limit=10")
        passed = response and "events" in response
        self.log_result("Replay Timeline", passed, "Missing events" if not passed else "")
        if passed:
            self.log(f"   Events count: {response.get('total_events', 0)}", "INFO")
        return passed
    
    def test_rebuild_state(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping rebuild_state - no case ID", "WARNING")
            return False
        response = self.request("GET", f"/rebuild/case/{self.test_case_id}/state")
        passed = response and "status" in response
        self.log_result("Rebuild State", passed, "Missing status" if not passed else "")
        return passed
    
    def test_verify_chain(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping verify_chain - no case ID", "WARNING")
            return False
        response = self.request("GET", f"/integrity/case/{self.test_case_id}")
        passed = response and "chain_valid" in response
        self.log_result("Verify Chain", passed, "Missing chain_valid" if not passed else "")
        if passed:
            self.log(f"   Chain valid: {response.get('chain_valid', False)}", "INFO")
        return passed
    
    # =========================================================
    # EVIDENCE TESTS
    # =========================================================
    
    def test_upload_evidence(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping upload_evidence - no case ID", "WARNING")
            return False
        
        # Create test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(f"Test evidence content from automated test at {datetime.now().isoformat()}")
            temp_file = f.name
        
        try:
            url = f"{self.base_url}/evidence/upload/{self.test_case_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            with open(temp_file, 'rb') as f:
                files = {"file": (f.name, f, "text/plain")}
                response = requests.post(url, headers=headers, files=files, timeout=30)
            
            import os
            os.unlink(temp_file)
            
            passed = response.status_code in [200, 201]
            if passed:
                data = response.json()
                self.test_evidence_id = data.get("id")
                self.log(f"   Evidence ID: {self.test_evidence_id}", "INFO")
            
            self.log_result("Upload Evidence", passed, "Upload failed" if not passed else "")
            return passed
        except Exception as e:
            self.log_result("Upload Evidence", False, str(e))
            return False
    
    def test_get_evidence(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping get_evidence - no case ID", "WARNING")
            return False
        response = self.request("GET", f"/evidence/case/{self.test_case_id}")
        passed = response and isinstance(response, list)
        self.log_result("Get Evidence List", passed, "Invalid response" if not passed else "")
        return passed
    
    def test_verify_evidence(self) -> bool:
        if not self.test_evidence_id:
            self.log("Skipping verify_evidence - no evidence ID", "WARNING")
            return False
        response = self.request("GET", f"/evidence/{self.test_evidence_id}/verify")
        passed = response and response.get("is_valid") == True
        self.log_result("Verify Evidence", passed, "Invalid integrity" if not passed else "")
        if passed:
            self.log(f"   Hash match: {response.get('is_valid', False)}", "INFO")
        return passed
    
    # =========================================================
    # FINDINGS TESTS
    # =========================================================
    
    def test_create_finding(self) -> bool:
        if not self.test_case_id or not self.test_evidence_id:
            self.log("Skipping create_finding - missing case or evidence", "WARNING")
            return False
        
        data = {
            "case_id": self.test_case_id,
            "title": "Automated Test Finding",
            "description": "Detected anomaly from automated testing",
            "evidence_ids": [self.test_evidence_id],
            "financial_loss": 100000000
        }
        response = self.request("POST", "/findings/create-from-evidence", data=data)
        passed = response and "id" in response
        self.log_result("Create Finding", passed, "Failed to create finding" if not passed else "")
        if passed:
            self.log(f"   Anomaly score: {response.get('anomaly_score', 0)}", "INFO")
            self.log(f"   Severity: {response.get('severity', 'unknown')}", "INFO")
        return passed
    
    def test_get_findings(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping get_findings - no case ID", "WARNING")
            return False
        response = self.request("GET", f"/findings/case/{self.test_case_id}")
        passed = response and isinstance(response, list)
        self.log_result("Get Findings List", passed, "Invalid response" if not passed else "")
        if passed:
            self.log(f"   Findings count: {len(response)}", "INFO")
        return passed
    
    def test_anomaly_calculate(self) -> bool:
        if not self.test_evidence_id:
            self.log("Skipping anomaly_calculate - no evidence ID", "WARNING")
            return False
        response = self.request("POST", "/findings/anomaly/calculate", data={"evidence_ids": [self.test_evidence_id]})
        passed = response and "anomaly_score" in response
        self.log_result("Calculate Anomaly", passed, "Missing anomaly_score" if not passed else "")
        if passed:
            self.log(f"   Anomaly score: {response.get('anomaly_score', 0)}", "INFO")
        return passed
    
    # =========================================================
    # GRAPH TESTS
    # =========================================================
    
    def test_graph_api(self) -> bool:
        response = self.request("GET", "/graph/test")
        passed = response and response.get("status") == "Graph API is working"
        self.log_result("Graph API Test", passed, "API not responding" if not passed else "")
        return passed
    
    def test_add_entity(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping add_entity - no case ID", "WARNING")
            return False
        
        data = {
            "entity_type": "person",
            "name": f"Test Entity {datetime.now().strftime('%H%M%S')}",
            "tax_id": "123456789"
        }
        response = self.request("POST", f"/graph/case/{self.test_case_id}/entity", data=data)
        passed = response and "id" in response
        self.log_result("Add Entity", passed, "Failed to add entity" if not passed else "")
        return passed
    
    def test_get_entities(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping get_entities - no case ID", "WARNING")
            return False
        response = self.request("GET", f"/graph/case/{self.test_case_id}/entities")
        passed = response and isinstance(response, list)
        self.log_result("Get Entities", passed, "Invalid response" if not passed else "")
        return passed
    
    def test_graph_data(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping graph_data - no case ID", "WARNING")
            return False
        response = self.request("GET", f"/graph/case/{self.test_case_id}/graph-data")
        passed = response and "nodes" in response and "edges" in response
        self.log_result("Graph Visualization Data", passed, "Missing nodes/edges" if not passed else "")
        if passed:
            self.log(f"   Nodes: {len(response.get('nodes', []))}, Edges: {len(response.get('edges', []))}", "INFO")
        return passed
    
    # =========================================================
    # TEMPORAL QUERY TESTS
    # =========================================================
    
    def test_temporal_trace_chain(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping trace_chain - no case ID", "WARNING")
            return False
        response = self.request("GET", f"/temporal/case/{self.test_case_id}/trace-chain")
        passed = response is not None
        self.log_result("Temporal Trace Chain", passed, "Endpoint not responding" if not passed else "")
        return passed
    
    def test_temporal_compare(self) -> bool:
        if not self.test_case_id:
            self.log("Skipping compare_versions - no case ID", "WARNING")
            return False
        response = self.request("GET", f"/temporal/case/{self.test_case_id}/compare?version_a=1&version_b=2")
        passed = response is not None
        self.log_result("Temporal Compare Versions", passed, "Endpoint not responding" if not passed else "")
        return passed
    
    # =========================================================
    # RUN ALL TESTS
    # =========================================================
    
    def run_all_tests(self):
        print("\n" + "="*60)
        print("  NEMESIS V8+ DASHBOARD ENDPOINT TESTING")
        print("="*60)
        print(f"Base URL: {self.base_url}")
        print(f"Time: {datetime.now().isoformat()}")
        print("="*60 + "\n")
        
        # Authentication first
        if not self.test_login():
            self.log("Authentication failed. Aborting tests.", "ERROR")
            self.print_summary()
            return
        
        # Run all tests
        tests = [
            ("Health Check", self.test_health),
            ("Root Endpoint", self.test_root),
            ("Dashboard Summary", self.test_dashboard_summary),
            ("Integrity Summary", self.test_integrity_summary),
            ("Findings Dashboard", self.test_findings_summary),
            ("Create Case", self.test_create_case),
            ("Get Cases", self.test_get_cases),
            ("Get Case Detail", self.test_get_case),
            ("Update Case Status", self.test_update_case_status),
            ("Assign Case", self.test_assign_case),
            ("Replay Timeline", self.test_replay_timeline),
            ("Rebuild State", self.test_rebuild_state),
            ("Verify Chain", self.test_verify_chain),
            ("Upload Evidence", self.test_upload_evidence),
            ("Get Evidence", self.test_get_evidence),
            ("Verify Evidence", self.test_verify_evidence),
            ("Calculate Anomaly", self.test_anomaly_calculate),
            ("Create Finding", self.test_create_finding),
            ("Get Findings", self.test_get_findings),
            ("Graph API Test", self.test_graph_api),
            ("Add Entity", self.test_add_entity),
            ("Get Entities", self.test_get_entities),
            ("Graph Data", self.test_graph_data),
            ("Temporal Trace Chain", self.test_temporal_trace_chain),
            ("Temporal Compare", self.test_temporal_compare),
        ]
        
        for name, test_func in tests:
            test_func()
            time.sleep(0.5)  # Small delay between tests
        
        self.print_summary()
    
    def print_summary(self):
        print("\n" + "="*60)
        print("  TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.results['total']}")
        print(f"{GREEN}Passed: {self.results['passed']}{RESET}")
        print(f"{RED}Failed: {self.results['failed']}{RESET}")
        
        if self.results['total'] > 0:
            pass_rate = (self.results['passed'] / self.results['total']) * 100
            print(f"Pass Rate: {pass_rate:.1f}%")
        
        print("="*60)
        
        if self.results['failed'] == 0:
            print(f"{GREEN}🎉 ALL TESTS PASSED! Dashboard endpoints are ready.{RESET}")
        else:
            print(f"{YELLOW}⚠️ {self.results['failed']} test(s) failed. Please check the errors above.{RESET}")
        
        print("="*60 + "\n")


def main():
    tester = DashboardTester()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--direct":
            tester.base_url = "http://localhost:8000"
            print("Using direct API: http://localhost:8000")
        elif sys.argv[1] == "--help":
            print("Usage: python test_dashboard_endpoints.py [--direct]")
            print("  --direct: Test against direct API (port 8000) instead of load balancer (port 80)")
            return
    
    tester.run_all_tests()


if __name__ == "__main__":
    main()
