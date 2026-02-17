# QA-FRAMEWORK Integration Tests

Comprehensive integration test suite for validating communication between the QA Framework core and Dashboard backend.

## Overview

This test suite ensures reliable bidirectional communication between:
- **Framework Core**: Test execution engine and adapters
- **Dashboard Backend**: FastAPI-based management API
- **Dashboard Frontend**: React-based user interface (tested via API)

## Directory Structure

```
tests/integration/
├── __init__.py
├── conftest.py                  # Shared fixtures and configuration
├── test_framework_dashboard.py  # Core integration tests
├── test_data_flow.py           # Data consistency tests
├── test_concurrent.py          # Concurrent operations
├── test_e2e_flows.py           # End-to-end scenarios
└── fixtures/
    ├── __init__.py
    ├── framework_fixtures.py   # Framework-specific fixtures
    └── dashboard_fixtures.py   # Dashboard-specific fixtures
```

## Test Categories

### 1. Core Integration Tests (`test_framework_dashboard.py`)

Tests bidirectional communication between Framework and Dashboard:

**Framework → Dashboard:**
- Test result transmission and display
- Execution status updates in real-time
- Test artifact storage and retrieval

**Dashboard → Framework:**
- Test case creation and reception
- Execution triggering and processing
- Configuration parameter application

**API Endpoints:**
- Authentication endpoints
- Suite CRUD operations
- Case CRUD operations
- Execution management

**Error Handling:**
- Dashboard unavailability handling
- Framework timeout handling
- Invalid data validation

**Real-Time Communication:**
- WebSocket connections
- Status updates broadcasting
- Multi-client updates

### 2. Data Flow Tests (`test_data_flow.py`)

Tests data consistency and integrity:

**Database Consistency:**
- Cross-component data consistency
- Foreign key constraints
- Cascade deletions

**Cache Consistency:**
- Write-read consistency
- Cache invalidation patterns
- TTL expiration handling
- Stampede protection

**Transaction Management:**
- Successful commits
- Rollback on errors
- Partial update handling
- Nested transactions

**Data Synchronization:**
- Framework to Dashboard sync
- Dashboard to Framework sync
- Bidirectional status sync

### 3. Concurrent Operations (`test_concurrent.py`)

Tests multi-user and parallel execution scenarios:

**Multi-User Operations:**
- Concurrent suite creation
- Concurrent case updates
- Concurrent execution triggers
- Concurrent dashboard reads

**Parallel Executions:**
- Multiple suite execution
- Concurrent artifact uploads
- Shared resource contention

**Resource Management:**
- Connection pool exhaustion
- Cache contention
- File system contention

**Deadlock Prevention:**
- Lock timeouts
- Resource hierarchy
- Try-lock patterns

**Race Conditions:**
- Read-modify-write atomicity
- Check-then-act safety
- Collection modification

### 4. End-to-End Flows (`test_e2e_flows.py`)

Tests complete business workflows:

**Test Lifecycle:**
- Create → Execute → Report → View
- Scheduled executions
- Regression testing with comparison

**Multi-User Workflows:**
- Collaborative editing
- Concurrent viewing
- Multi-tenant isolation

**Real-Time Features:**
- Progress updates
- Live log streaming
- WebSocket reconnection
- Multi-channel subscriptions

**Error Recovery:**
- Execution failure recovery
- Database connection recovery
- Partial result handling
- Configuration error recovery

**External Integrations:**
- Jira bug creation
- Zephyr synchronization
- Notification delivery

## Running the Tests

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r dashboard/backend/requirements.txt
pip install pytest-asyncio pytest-xdist testcontainers
```

### Basic Usage

```bash
# Run all integration tests
cd /home/ubuntu/.openclaw/workspace/QA-FRAMEWORK
pytest tests/integration/ -v

# Run with coverage
pytest tests/integration/ --cov=src --cov=dashboard --cov-report=html

# Run specific test file
pytest tests/integration/test_framework_dashboard.py -v

# Run specific test class
pytest tests/integration/test_framework_dashboard.py::TestFrameworkToDashboardIntegration -v

# Run specific test method
pytest tests/integration/test_framework_dashboard.py::TestFrameworkToDashboardIntegration::test_framework_generates_results_dashboard_displays -v
```

### Using Markers

```bash
# Run only integration tests
pytest tests/ -m integration -v

# Run only database tests
pytest tests/ -m database -v

# Run only concurrent tests
pytest tests/ -m concurrent -v

# Run only end-to-end tests
pytest tests/ -m e2e -v

# Run only WebSocket tests
pytest tests/ -m websocket -v

# Exclude slow tests
pytest tests/integration/ -m "not slow" -v

# Run multiple markers
pytest tests/ -m "integration and database" -v
```

### Parallel Execution

```bash
# Run tests in parallel (2 workers)
pytest tests/integration/ -n 2 -v

# Auto-detect number of workers
pytest tests/integration/ -n auto -v
```

### Environment Variables

```bash
# Configure test database
export TEST_POSTGRES_HOST=localhost
export TEST_POSTGRES_PORT=5432
export TEST_POSTGRES_DB=qa_framework_test
export TEST_POSTGRES_USER=qa_user
export TEST_POSTGRES_PASSWORD=qa_password

# Configure test Redis
export TEST_REDIS_HOST=localhost
export TEST_REDIS_PORT=6379
export TEST_REDIS_DB=1

# Configure backend URL
export TEST_BACKEND_URL=http://localhost:8000

# Run tests
pytest tests/integration/ -v
```

## Configuration

### conftest.py Options

The `conftest.py` file provides several configuration options:

```python
class TestConfig:
    # Database configuration
    POSTGRES_HOST = os.getenv('TEST_POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.getenv('TEST_POSTGRES_PORT', '5432'))
    
    # Redis configuration
    REDIS_HOST = os.getenv('TEST_REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('TEST_REDIS_PORT', '6379'))
    
    # Backend configuration
    BACKEND_URL = os.getenv('TEST_BACKEND_URL', 'http://localhost:8000')
    
    # Test timeouts
    DEFAULT_TIMEOUT = 30
    WEBSOCKET_TIMEOUT = 5
```

### Performance Thresholds

Default performance thresholds are defined in fixtures:

```python
{
    "api_response_ms": 500,
    "database_query_ms": 100,
    "cache_operation_ms": 50,
    "websocket_message_ms": 100,
    "end_to_end_flow_s": 30
}
```

## Fixtures

### Shared Fixtures (conftest.py)

| Fixture | Description |
|---------|-------------|
| `db_engine` | Database engine for test session |
| `db_session` | Database session with auto-rollback |
| `http_client` | Async HTTP client for API testing |
| `authenticated_client` | Authenticated HTTP client |
| `redis_client` | Mock Redis client |
| `test_suite_data` | Factory for test suite data |
| `test_case_data` | Factory for test case data |
| `test_execution_data` | Factory for execution data |
| `user_data` | Factory for user data |
| `benchmark` | Performance benchmark utility |

### Framework Fixtures

| Fixture | Description |
|---------|-------------|
| `test_result_factory` | Creates TestResult entities |
| `test_runner` | Configured TestRunner instance |
| `mock_http_adapter` | Mock HTTP adapter |
| `mock_ui_adapter` | Mock Playwright adapter |
| `framework_config` | Framework configuration |

### Dashboard Fixtures

| Fixture | Description |
|---------|-------------|
| `user_model_factory` | Creates User model data |
| `test_suite_model_factory` | Creates TestSuite model data |
| `mock_execution_service` | Mock execution service |
| `mock_dashboard_cache` | Mock cache manager |
| `mock_websocket_manager` | Mock WebSocket manager |

## Test Markers

| Marker | Description |
|--------|-------------|
| `integration` | Integration tests |
| `database` | Tests requiring database |
| `redis` | Tests requiring Redis |
| `websocket` | Tests requiring WebSocket |
| `concurrent` | Concurrent operation tests |
| `e2e` | End-to-end tests |
| `slow` | Slow-running tests |

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: qa_framework_test
          POSTGRES_USER: qa_user
          POSTGRES_PASSWORD: qa_password
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r dashboard/backend/requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run integration tests
        env:
          TEST_POSTGRES_HOST: localhost
          TEST_REDIS_HOST: localhost
        run: |
          pytest tests/integration/ -v --cov=src --cov=dashboard \
            --cov-report=xml --cov-report=html
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```
psycopg2.OperationalError: connection refused
```

**Solution:**
```bash
# Ensure PostgreSQL is running
docker-compose up -d postgres

# Or use testcontainers (automatic)
```

#### 2. Redis Connection Errors

```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solution:**
```bash
# Ensure Redis is running
docker-compose up -d redis

# Check Redis connection
redis-cli ping
```

#### 3. Backend Not Responding

```
httpx.ConnectError: [Errno 111] Connection refused
```

**Solution:**
```bash
# Start backend server
cd dashboard/backend
uvicorn main:app --reload --port 8000
```

#### 4. Event Loop Issues

```
RuntimeError: Event loop is closed
```

**Solution:**
Ensure pytest-asyncio is configured correctly in `conftest.py`:
```python
pytestmark = pytest.mark.asyncio(loop_scope="function")
```

#### 5. Import Errors

```
ModuleNotFoundError: No module named 'dashboard'
```

**Solution:**
```bash
# Install all dependencies
pip install -e .
pip install -r dashboard/backend/requirements.txt
```

### Debug Mode

```bash
# Run with detailed output
pytest tests/integration/ -v -s --tb=long

# Run with debugger on failure
pytest tests/integration/ --pdb

# Run specific test with debug logging
pytest tests/integration/test_framework_dashboard.py -v -s \
  --log-cli-level=DEBUG
```

## Contributing

### Adding New Tests

1. Create test function in appropriate file
2. Use existing fixtures or create new ones
3. Add appropriate markers
4. Document the test purpose
5. Ensure idempotency

Example:
```python
@pytest.mark.integration
@pytest.mark.database
async def test_new_feature(
    authenticated_client,
    db_session
):
    """
    Test: Description of what this tests.
    
    Scenario:
    1. Step 1
    2. Step 2
    3. Expected result
    """
    # Test implementation
```

### Test Naming Conventions

- Use descriptive names: `test_<action>_<expected_result>`
- Group related tests in classes
- Use docstrings to describe test scenarios

## Performance Benchmarks

Expected performance metrics:

| Operation | Target | Threshold |
|-----------|--------|-----------|
| API Response | < 200ms | 500ms |
| DB Query | < 50ms | 100ms |
| Cache Op | < 10ms | 50ms |
| E2E Flow | < 10s | 30s |

## Coverage Requirements

- Minimum 80% code coverage
- 100% coverage for critical paths
- Integration tests should cover all API endpoints

## License

Same as QA-FRAMEWORK project
