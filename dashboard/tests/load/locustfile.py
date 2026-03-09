"""
Load Testing with Locust

Simulates:
- 100 concurrent users
- 1,000 requests/min
- Peak load scenarios
"""

from locust import HttpUser, task, between
import random


class QAFrameworkUser(HttpUser):
    """Simulates QA-FRAMEWORK user behavior"""
    
    wait_time = between(1, 3)
    
    @task(3)
    def view_dashboard(self):
        """View dashboard (most common)"""
        self.client.get("/api/v1/dashboard/stats")
    
    @task(2)
    def list_suites(self):
        """List test suites"""
        self.client.get("/api/v1/suites")
    
    @task(1)
    def create_suite(self):
        """Create test suite"""
        self.client.post("/api/v1/suites", json={
            "name": f"Load Test Suite {random.randint(1, 1000)}",
            "description": "Created during load testing",
            "framework_type": "pytest"
        })
    
    @task(2)
    def list_executions(self):
        """List test executions"""
        self.client.get("/api/v1/executions")
    
    @task(1)
    def view_health(self):
        """Health check"""
        self.client.get("/health")


# Run with: locust -f locustfile.py --host=https://qa-framework-backend.railway.app
# Open: http://localhost:8089
