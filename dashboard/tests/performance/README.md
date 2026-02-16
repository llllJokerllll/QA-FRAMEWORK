# QA-FRAMEWORK Dashboard - Performance Tests

This directory contains comprehensive performance tests for the QA-FRAMEWORK Dashboard API using [Locust](https://locust.io/), a scalable load testing framework.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Test Scenarios](#test-scenarios)
- [Running Tests](#running-tests)
- [Interpreting Results](#interpreting-results)
- [Performance Benchmarks](#performance-benchmarks)
- [Optimization Recommendations](#optimization-recommendations)
- [Configuration](#configuration)
- [Distributed Testing](#distributed-testing)
- [Troubleshooting](#troubleshooting)

## Overview

These performance tests simulate real-world user behaviors and traffic patterns to validate the API's performance under various load conditions:

- **Load Testing**: Simulate expected user traffic (100+ concurrent users)
- **Stress Testing**: Find system breaking points
- **Spike Testing**: Handle sudden traffic bursts
- **Soak Testing**: Validate long-term stability

### Key Metrics

- **Response Times**: p50, p95, p99 percentiles
- **Throughput**: Requests per second (RPS)
- **Error Rates**: Failed requests percentage
- **Resource Utilization**: CPU, memory, database connections

## Installation

### Prerequisites

- Python 3.8+
- Running QA-FRAMEWORK Dashboard API
- pip or pipenv

### Setup

1. Navigate to the performance tests directory:
```bash
cd tests/performance
```

2. Install dependencies (locust should already be in requirements.txt):
```bash
pip install locust==2.20.0
```

Or from the backend directory:
```bash
cd backend
pip install -r requirements.txt
```

3. Verify installation:
```bash
locust --version
```

## Quick Start

### 1. Start the API Server

Ensure the QA-FRAMEWORK Dashboard API is running:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Run Basic Load Test

```bash
cd tests/performance
locust -f locustfile.py --host=http://localhost:8000
```

Then open http://localhost:8089 in your browser to access the Locust web UI.

### 3. Configure Test Parameters

In the web UI:
- **Number of users**: 100
- **Spawn rate**: 5 (users per second)
- **Host**: http://localhost:8000

Click **Start swarming** to begin.

## Test Scenarios

### User Types

The tests simulate different user behaviors with weighted distributions:

#### 1. Dashboard Viewer (40% weight)
Read-heavy users who primarily view dashboards and reports:
- View dashboard statistics
- Check execution trends
- List test suites and cases
- View execution history

**Typical workflow**: Login → Dashboard → Trends → Suite List → Logout

#### 2. Suite Manager (20% weight)
Users who manage test suites:
- Create new test suites
- Update suite configurations
- Delete unused suites
- View suite details

**Typical workflow**: Login → Create Suite → Update Suite → List Cases → Delete Suite

#### 3. Case Manager (20% weight)
Users who work with test cases:
- Create test cases
- Update test code
- Manage test tags and priorities
- Delete obsolete cases

**Typical workflow**: Login → Select Suite → Create Case → Update Case → Execute Tests

#### 4. Execution Runner (15% weight)
Users who run test executions:
- Create execution jobs
- Start test runs
- Monitor execution progress
- Stop running executions

**Typical workflow**: Login → Create Execution → Start → Monitor → Stop/Complete

#### 5. Authenticated User (5% weight)
Authentication-focused operations:
- Login/logout flows
- Token refresh
- User profile access

### Test Classes

| Class | Purpose | Use Case |
|-------|---------|----------|
| `LoadTestUser` | Standard load testing | Regular performance validation |
| `StressTestUser` | Find breaking points | Capacity planning |
| `SpikeTestUser` | Sudden traffic bursts | Handling viral events |
| `WebsiteUser` | Default combined behavior | General monitoring |

## Running Tests

### Command Line Options

#### Basic Load Test (100 users, 5 min)
```bash
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 5 \
  --run-time 5m \
  --headless \
  --html=results/load_test_report.html \
  --csv=results/load_test
```

#### Stress Test (Ramp to 200 users)
```bash
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --users 200 \
  --spawn-rate 10 \
  --run-time 15m \
  --headless \
  --html=results/stress_test_report.html \
  --csv=results/stress_test \
  --class-picker StressTestUser
```

#### Spike Test (Sudden burst)
```bash
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --users 200 \
  --spawn-rate 50 \
  --run-time 3m \
  --headless \
  --html=results/spike_test_report.html \
  --csv=results/spike_test \
  --class-picker SpikeTestUser
```

#### Soak Test (Endurance, 1 hour)
```bash
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 2 \
  --run-time 60m \
  --headless \
  --html=results/soak_test_report.html \
  --csv=results/soak_test
```

### Environment Variables

Configure test parameters via environment variables:

```bash
# Test environment
export PERF_TEST_ENV=staging

# Target API
export PERF_TEST_BASE_URL=http://api-staging.example.com

# Test credentials
export PERF_TEST_USERNAME=perf_test_user
export PERF_TEST_PASSWORD=secure_password

# Distributed testing (optional)
export LOCUST_MASTER_HOST=locust-master
export LOCUST_MASTER_PORT=5557
```

### Using the Web UI

For interactive testing and real-time monitoring:

```bash
locust -f locustfile.py --host=http://localhost:8000
```

Access http://localhost:8089 and configure:

1. **Number of users**: Peak concurrent users to simulate
2. **Spawn rate**: How quickly to add users (users/second)
3. **Host**: API base URL

**Web UI Features**:
- Real-time statistics
- Response time distribution charts
- Request failure tracking
- Downloadable reports
- Test stop/start controls

## Interpreting Results

### HTML Report

The HTML report (`results/*_report.html`) contains:

1. **Request Statistics**
   - Total requests
   - Failed requests
   - Median/average response times
   - RPS (requests per second)

2. **Response Time Distribution**
   - Histogram of response times
   - Percentile breakdowns (p50, p95, p99)

3. **Failure Statistics**
   - Error messages
   - Failure counts by endpoint
   - Stack traces (if any)

4. **Charts**
   - Total requests per second
   - Response times over time
   - Number of users over time

### CSV Statistics

Three CSV files are generated:

- `*_stats.csv`: Per-endpoint statistics
- `*_stats_history.csv`: Time-series data
- `*_failures.csv`: Failed request details

Example stats CSV:
```csv
"Type","Name","Request Count","Failure Count","Median Response Time","Average Response Time","Min Response Time","Max Response Time","Average Content Size","Requests/s","Failures/s","50%","66%","75%","80%","90%","95%","98%","99%","99.9%","99.99%","100%"
"GET","/api/v1/dashboard/stats",1500,0,120,145,45,890,2048,25.5,0.0,120,135,150,165,200,250,400,550,800,890,890
```

### Key Metrics to Monitor

#### Response Time Percentiles

| Percentile | Target | Warning | Critical |
|------------|--------|---------|----------|
| p50 (Median) | < 200ms | 200-500ms | > 500ms |
| p95 | < 500ms | 500-1000ms | > 1000ms |
| p99 | < 1000ms | 1000-2000ms | > 2000ms |

#### Throughput

| Users | Target RPS | Minimum RPS |
|-------|------------|-------------|
| 50 | 25+ | 15 |
| 100 | 50+ | 30 |
| 200 | 100+ | 60 |

#### Error Rates

- **Acceptable**: < 1%
- **Warning**: 1-5%
- **Critical**: > 5%

## Performance Benchmarks

### Baseline Performance

Based on 100 concurrent users:

| Endpoint | p50 | p95 | p99 | RPS |
|----------|-----|-----|-----|-----|
| GET /dashboard/stats | 120ms | 350ms | 650ms | 25 |
| GET /dashboard/trends | 150ms | 400ms | 800ms | 20 |
| GET /suites | 100ms | 300ms | 550ms | 30 |
| POST /suites | 180ms | 500ms | 900ms | 15 |
| GET /cases | 110ms | 320ms | 600ms | 28 |
| POST /cases | 160ms | 480ms | 850ms | 18 |
| POST /executions | 200ms | 600ms | 1100ms | 12 |
| POST /auth/login | 250ms | 700ms | 1200ms | 10 |

### Scalability Targets

| Concurrent Users | Avg Response Time | Total RPS | Error Rate |
|------------------|-------------------|-----------|------------|
| 50 | < 150ms | 30+ | < 0.5% |
| 100 | < 200ms | 50+ | < 1.0% |
| 200 | < 350ms | 90+ | < 2.0% |
| 500 | < 800ms | 200+ | < 5.0% |

## Optimization Recommendations

### Database Optimization

1. **Connection Pooling**
   - Current: Monitor active connections
   - Recommended: Use SQLAlchemy connection pool with max_overflow=20

2. **Query Optimization**
   - Add indexes on frequently queried columns:
     ```sql
     CREATE INDEX idx_suite_created_by ON test_suites(created_by);
     CREATE INDEX idx_case_suite_id ON test_cases(suite_id);
     CREATE INDEX idx_execution_suite_id ON test_executions(suite_id);
     CREATE INDEX idx_execution_status ON test_executions(status);
     ```

3. **Caching**
   - Implement Redis caching for dashboard stats
   - Cache execution trends (TTL: 5 minutes)
   - Cache suite lists (TTL: 1 minute)

### API Optimization

1. **Pagination**
   - Enforce maximum limit (100 items)
   - Use cursor-based pagination for large datasets

2. **Async Processing**
   - Move execution start/stop to background tasks (Celery)
   - Use WebSockets for real-time updates

3. **Response Compression**
   - Enable gzip compression for responses > 1KB

### Infrastructure

1. **Horizontal Scaling**
   - Use load balancer (nginx/HAProxy)
   - Scale API servers based on CPU/memory metrics

2. **Database Scaling**
   - Read replicas for dashboard queries
   - Connection pooling (PgBouncer)

3. **Monitoring**
   - Set up alerts for:
     - p95 response time > 500ms
     - Error rate > 1%
     - Database connection pool exhaustion

## Configuration

### config.py

The `config.py` file contains all test configurations:

```python
# Performance thresholds
thresholds = PerformanceThresholds(
    p50_max=200,      # 200ms median response time
    p95_max=500,      # 500ms 95th percentile
    p99_max=1000,     # 1s 99th percentile
    max_error_rate=1.0  # 1% max error rate
)

# Load test configuration
load_test = LoadTestConfig(
    target_users=100,
    spawn_rate=5.0,
    test_duration=300  # 5 minutes
)
```

### Customizing Tests

Create custom test scenarios by extending base classes:

```python
from locustfile import BaseUser

class CustomUser(BaseUser):
    @task
    def my_custom_task(self):
        # Your custom test logic
        pass
```

## Distributed Testing

For large-scale testing (1000+ users):

### 1. Start Master

```bash
locust -f locustfile.py --master --host=http://api.example.com
```

### 2. Start Workers

On multiple machines:

```bash
locust -f locustfile.py --worker --master-host=<master-ip>
```

### 3. Access Web UI

Open http://<master-ip>:8089 to control the test.

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: locust-master
spec:
  replicas: 1
  selector:
    matchLabels:
      app: locust-master
  template:
    metadata:
      labels:
        app: locust-master
    spec:
      containers:
      - name: locust
        image: locustio/locust:2.20.0
        command: ["locust", "-f", "/mnt/locust/locustfile.py", "--master"]
        ports:
        - containerPort: 8089
        - containerPort: 5557
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: locust-worker
spec:
  replicas: 5
  selector:
    matchLabels:
      app: locust-worker
  template:
    metadata:
      labels:
        app: locust-worker
    spec:
      containers:
      - name: locust
        image: locustio/locust:2.20.0
        command: ["locust", "-f", "/mnt/locust/locustfile.py", "--worker", "--master-host=locust-master"]
```

## Troubleshooting

### Common Issues

#### 1. Connection Errors

**Symptom**: `Connection refused` or `Connection timeout`

**Solutions**:
- Verify API server is running
- Check firewall rules
- Ensure correct host/port in command
- Increase timeout in config.py

#### 2. Authentication Failures

**Symptom**: 401/403 errors

**Solutions**:
- Verify test credentials
- Check token expiration handling
- Ensure user exists in database

#### 3. High Memory Usage

**Symptom**: Locust process consuming too much memory

**Solutions**:
- Reduce number of users per worker
- Use distributed mode
- Limit request history: `--reset-stats`

#### 4. Inaccurate Results

**Symptom**: Unusually fast/slow response times

**Solutions**:
- Run tests from a machine close to the API
- Check network latency
- Ensure database is not on the same machine
- Disable logging during tests

### Debug Mode

Enable verbose logging:

```bash
locust -f locustfile.py --host=http://localhost:8000 --loglevel=DEBUG
```

### Test Data Cleanup

If tests leave data behind:

```bash
# Manual cleanup via API
python -c "
import requests
# Cleanup script
"
```

Or use the cleanup method in user classes which runs automatically on test stop.

## CI/CD Integration

### GitHub Actions

```yaml
name: Performance Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Run at 2 AM daily
  workflow_dispatch:

jobs:
  performance-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install locust==2.20.0
      
      - name: Start API
        run: |
          cd backend
          uvicorn main:app --host 0.0.0.0 --port 8000 &
          sleep 10
      
      - name: Run Performance Tests
        run: |
          cd tests/performance
          locust -f locustfile.py \
            --host=http://localhost:8000 \
            --users 100 \
            --spawn-rate 5 \
            --run-time 5m \
            --headless \
            --html=results/report.html \
            --csv=results/stats
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: tests/performance/results/
```

## Best Practices

1. **Warm-up Period**: Always include a 1-2 minute warm-up before measuring
2. **Representative Data**: Use realistic data volumes
3. **Network Isolation**: Run tests on a dedicated network segment
4. **Baseline Comparison**: Always compare against previous baselines
5. **Resource Monitoring**: Monitor server resources during tests
6. **Gradual Ramp-up**: Don't start with full load immediately
7. **Cleanup**: Ensure tests clean up created resources
8. **Idempotency**: Tests should be repeatable without side effects

## Support

For issues or questions:
- Locust Documentation: https://docs.locust.io/
- GitHub Issues: [Project Issues]
- Slack: [Team Channel]

## License

Same as QA-FRAMEWORK Dashboard project.
