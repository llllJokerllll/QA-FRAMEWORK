"""
Business Metrics for QA-Framework
Track and expose business-specific metrics for Prometheus
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from typing import Optional
import time
from contextlib import contextmanager


# ============================================================================
# COUNTER METRICS (Cumulative counts)
# ============================================================================

# Test execution metrics
tests_executed_total = Counter(
    'qa_tests_executed_total',
    'Total number of tests executed',
    ['suite_id', 'status', 'framework']  # labels: passed, failed, skipped
)

test_failures_total = Counter(
    'qa_test_failures_total',
    'Total number of test failures',
    ['suite_id', 'error_type']
)

# User activity metrics
user_actions_total = Counter(
    'qa_user_actions_total',
    'Total user actions',
    ['user_id', 'action_type']  # create_suite, run_test, view_report, etc.
)

# API usage metrics
api_requests_total = Counter(
    'qa_api_requests_total',
    'Total API requests',
    ['endpoint', 'method', 'status_code']
)

# Suite creation metrics
suites_created_total = Counter(
    'qa_suites_created_total',
    'Total test suites created',
    ['user_id']
)

# ============================================================================
# HISTOGRAM METRICS (Distribution of values)
# ============================================================================

# Test execution duration
test_duration_seconds = Histogram(
    'qa_test_duration_seconds',
    'Test execution duration in seconds',
    ['suite_id', 'framework'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

# API response time
api_response_time_seconds = Histogram(
    'qa_api_response_time_seconds',
    'API response time in seconds',
    ['endpoint', 'method'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# Suite execution time
suite_execution_seconds = Histogram(
    'qa_suite_execution_seconds',
    'Test suite execution time in seconds',
    ['suite_id'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0, 1800.0, 3600.0]
)

# ============================================================================
# GAUGE METRICS (Current values)
# ============================================================================

# Active users
active_users_gauge = Gauge(
    'qa_active_users',
    'Number of currently active users'
)

# Test success rate (last hour)
test_success_rate_gauge = Gauge(
    'qa_test_success_rate',
    'Test success rate percentage (last hour)',
    ['suite_id']
)

# Error rate
error_rate_gauge = Gauge(
    'qa_error_rate',
    'Error rate percentage (last hour)',
    ['error_type']
)

# Queue size (pending tests)
queue_size_gauge = Gauge(
    'qa_pending_tests_queue_size',
    'Number of tests waiting in queue'
)

# System load
system_load_gauge = Gauge(
    'qa_system_load',
    'System load average',
    ['period']  # 1m, 5m, 15m
)


# ============================================================================
# METRICS MANAGER
# ============================================================================

class BusinessMetricsManager:
    """Manager for business metrics tracking."""
    
    def __init__(self):
        self.start_times: dict = {}
    
    def track_test_execution(self, suite_id: str, framework: str = "pytest"):
        """
        Context manager to track test execution.
        
        Usage:
            with metrics.track_test_execution("suite_123"):
                run_tests()
        """
        return TestExecutionTracker(self, suite_id, framework)
    
    def track_api_request(self, endpoint: str, method: str):
        """
        Context manager to track API request.
        
        Usage:
            with metrics.track_api_request("/api/v1/suites", "POST"):
                process_request()
        """
        return APIRequestTracker(self, endpoint, method)
    
    def record_user_action(self, user_id: str, action_type: str):
        """Record a user action."""
        user_actions_total.labels(user_id=user_id, action_type=action_type).inc()
    
    def record_test_result(self, suite_id: str, status: str, framework: str = "pytest"):
        """Record a test result."""
        tests_executed_total.labels(
            suite_id=suite_id,
            status=status,
            framework=framework
        ).inc()
        
        if status == "failed":
            test_failures_total.labels(suite_id=suite_id, error_type="assertion").inc()
    
    def update_active_users(self, count: int):
        """Update active users count."""
        active_users_gauge.set(count)
    
    def update_success_rate(self, suite_id: str, rate: float):
        """Update test success rate for a suite."""
        test_success_rate_gauge.labels(suite_id=suite_id).set(rate)
    
    def update_error_rate(self, error_type: str, rate: float):
        """Update error rate."""
        error_rate_gauge.labels(error_type=error_type).set(rate)
    
    def update_queue_size(self, size: int):
        """Update pending tests queue size."""
        queue_size_gauge.set(size)
    
    def update_system_load(self, load_1m: float, load_5m: float, load_15m: float):
        """Update system load metrics."""
        system_load_gauge.labels(period='1m').set(load_1m)
        system_load_gauge.labels(period='5m').set(load_5m)
        system_load_gauge.labels(period='15m').set(load_15m)


class TestExecutionTracker:
    """Context manager for tracking test execution."""
    
    def __init__(self, metrics: BusinessMetricsManager, suite_id: str, framework: str):
        self.metrics = metrics
        self.suite_id = suite_id
        self.framework = framework
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        test_duration_seconds.labels(
            suite_id=self.suite_id,
            framework=self.framework
        ).observe(duration)
        
        suite_execution_seconds.labels(suite_id=self.suite_id).observe(duration)
        
        if exc_type is not None:
            self.metrics.record_test_result(
                self.suite_id,
                "failed",
                self.framework
            )
        else:
            self.metrics.record_test_result(
                self.suite_id,
                "passed",
                self.framework
            )


class APIRequestTracker:
    """Context manager for tracking API requests."""
    
    def __init__(self, metrics: BusinessMetricsManager, endpoint: str, method: str):
        self.metrics = metrics
        self.endpoint = endpoint
        self.method = method
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        api_response_time_seconds.labels(
            endpoint=self.endpoint,
            method=self.method
        ).observe(duration)
        
        status_code = "500" if exc_type else "200"
        api_requests_total.labels(
            endpoint=self.endpoint,
            method=self.method,
            status_code=status_code
        ).inc()


# Create global metrics manager instance
metrics_manager = BusinessMetricsManager()


def get_metrics_response() -> Response:
    """Generate Prometheus metrics response."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
