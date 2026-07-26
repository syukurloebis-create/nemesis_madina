"""
NEMESIS Madina - Load Test
✅ Performance verification with locust
"""

from locust import HttpUser, task, between
import random
import uuid


class NEMESISUser(HttpUser):
    """Load test user."""
    
    wait_time = between(0.5, 2.0)
    
    def on_start(self):
        """Start test."""
        self.case_ids = []
    
    @task(3)
    def analyze_case(self):
        """Analyze case endpoint."""
        case_id = str(uuid.uuid4())
        payload = {
            "case_id": case_id,
            "fraud_analysis": {
                "score": random.uniform(0.5, 1.0),
                "patterns": ["unusual_amount", "velocity_breach"],
                "confidence": random.uniform(0.8, 0.99),
            }
        }
        
        with self.client.post("/api/v1/cases/analyze", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                self.case_ids.append(case_id)
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def get_dashboard(self):
        """Get dashboard endpoint."""
        if not self.case_ids:
            return
        
        case_id = random.choice(self.case_ids)
        with self.client.get(f"/api/v1/dashboard/{case_id}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def get_metrics(self):
        """Get metrics endpoint."""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")