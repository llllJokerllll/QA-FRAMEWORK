# QA-FRAMEWORK

<p align="center">
  <h1>🚀 Modern QA Automation Framework</h1>
  <p><strong>Python 3.12 | Clean Architecture | SOLID Principles</strong></p>
</p>

---

## 📋 Overview

**QA-FRAMEWORK** is a comprehensive, modern testing framework for automating all types of QA tests. Built with Clean Architecture and SOLID principles, it provides a robust foundation for API, UI, integration, and end-to-end testing.

### ✨ Key Features

- 🏗️ **Clean Architecture** - Separation of concerns and maintainability
- 🎯 **SOLID Principles** - Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- 🧪 **Multi-Type Testing** - API, UI, Integration, E2E, Performance, Security, Database
- 🚀 **Async Support** - Full async/await support with HTTPX and Playwright
- 📊 **Advanced Reporting** - Allure, HTML, JSON reports with screenshots/videos
- ⚡ **Parallel Execution** - pytest-xdist for faster test runs
- 🔧 **Flexible Configuration** - YAML/JSON/ENV configuration support
- 🧱 **Type Safety** - 100% type hints with Pydantic
- 📝 **Comprehensive Documentation** - Docstrings and examples
- 🔄 **CI/CD Ready** - GitHub Actions and Docker support
- 🛡️ **Security Testing** - SQL injection, XSS, authentication, rate limiting
- ⚡ **Performance Testing** - Load testing, benchmarks, metrics collection
- 🗄️ **Database Testing** - Data integrity, migrations, SQL validation

---

## 🎯 Supported Testing Types

| Type | Tools | Status |
|------|-------|--------|
| **API Testing** | HTTPX, Requests | ✅ Supported |
| **UI Testing** | Playwright | ✅ Supported |
| **Integration Testing** | Pytest | ✅ Supported |
| **E2E Testing** | Playwright | ✅ Supported |
| **Performance Testing** | Locust, K6, Apache Bench | ✅ Supported |
| **Security Testing** | SQL Injection, XSS, Auth Testing | ✅ Supported |
| **Database Testing** | SQLite, PostgreSQL, MySQL | ✅ Supported |
| **Reporting** | Allure, HTML, JSON | ✅ Supported |

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/qa-framework.git
cd qa-framework

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e ".[dev,ui,performance,security]"

# Install Playwright browsers (for UI testing)
playwright install
```

### Run Your First Test

```python
# tests/api/test_users_api.py
import pytest
from src.adapters.http.httpx_client import HTTPXClient


@pytest.mark.asyncio
async def test_get_users():
    """Test getting users from API."""
    client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
    
    response = await client.get("/users")
    
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert isinstance(response.json(), list)
```

Run the test:
```bash
pytest tests/api/test_users_api.py -v
```

---

## 💡 Usage Examples

### API Testing Example

```python
# tests/api/test_users_api.py
import pytest
from src.adapters.http.httpx_client import HTTPXClient


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_users():
    """Test getting users from API."""
    client = HTTPXClient(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=30
    )
    
    response = await client.get("/users")
    
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert isinstance(response.json(), list)
```

Run test:
```bash
pytest tests/api/test_users_api.py -v
```

### UI Testing Example (Playwright)

```python
# tests/ui/test_login_page.py
import pytest
from src.adapters.ui.playwright_page import PlaywrightPage


@pytest.mark.ui
@pytest.mark.asyncio
async def test_user_login():
    """Test user login flow."""
    async with PlaywrightPage("chromium", headless=True) as page:
        await page.goto("https://example.com/login")
        await page.fill("#username", "testuser")
        await page.fill("#password", "testpass")
        await page.click("#login-button")
        
        # Assertions
        await page.wait_for_selector("#dashboard")
        assert await page.is_visible("#welcome-message")
```

---

## 📁 Project Structure

```
qa-framework/
├── src/
│   ├── core/                     # Core business logic
│   │   ├── interfaces/          # Interfaces/Contracts (SOLID DIP)
│   │   ├── entities/            # Domain entities
│   │   ├── use_cases/           # Application logic (SOLID SRP)
│   │   └── repositories/        # Data access
│   ├── adapters/                # External integrations
│   │   ├── http/              # HTTPX, Requests
│   │   ├── ui/                # Playwright, Selenium
│   │   ├── reporting/         # Allure, HTML, JSON
│   │   ├── performance/       # Locust, K6, Apache Bench
│   │   ├── security/          # SQL Injection, XSS, Auth, Rate Limit
│   │   └── database/          # Database testing, SQL validation
│   └── infrastructure/         # Cross-cutting concerns
│       ├── config/           # Configuration
│       ├── logger/           # Logging
│       └── utils/            # Utilities
├── tests/                       # Test suites
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   ├── e2e/                  # E2E tests
│   └── fixtures/             # Pytest fixtures
├── docs/                        # Documentation
├── examples/                    # Usage examples
├── config/                      # Configuration files
├── requirements.txt            # Dependencies
├── setup.py                    # Package setup
├── pyproject.toml              # Tool configuration
└── README.md                   # This file
```

---

## 💡 Usage Examples

### API Testing Example

```python
# tests/api/test_api_example.py
import pytest
from src.adapters.http.httpx_client import HTTPXClient
from src.core.entities.test_result import TestResult


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_user():
    """Test creating a new user via API."""
    client = HTTPXClient(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=30
    )
    
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }
    
    response = await client.post("/users", json=user_data)
    
    result = TestResult(
        test_name="test_create_user",
        passed=response.status_code == 201,
        response=response.json(),
        execution_time=1.5
    )
    
    assert result.passed
    assert response.json()["name"] == "Test User"
```

### Parallel API Testing Example

```python
# tests/api/test_parallel_api.py
import pytest
from typing import Dict, Any


@pytest.mark.api
@pytest.mark.parallel_safe
@pytest.mark.asyncio
async def test_parallel_api_calls(async_http_client):
    """Test API calls run safely in parallel."""
    response = await async_http_client.get("/users")
    assert response.status_code == 200


@pytest.mark.api
@pytest.mark.parallel_safe
def test_api_with_isolation(http_client, isolated_test_data: Dict[str, Any]):
    """Test with isolated data per test."""
    response = http_client.get("/users/1")
    isolated_test_data["user"] = response.json()
    assert response.status_code == 200
```

### Parallel UI Testing Example

```python
# tests/ui/test_parallel_ui.py
import pytest
from typing import Dict, Any


@pytest.mark.ui
@pytest.mark.parallel_safe
@pytest.mark.asyncio
async def test_parallel_ui_1(page):
    """Test UI with isolated page instance."""
    await page.goto("https://example.com")
    assert await page.title() == "Example Domain"


@pytest.mark.ui
@pytest.mark.parallel_safe
@pytest.mark.asyncio
async def test_parallel_ui_2(page):
    """Another UI test running in parallel."""
    await page.goto("https://example.org")
    assert await page.title() == "Example Domain"
```

### UI Testing Example (Playwright)

```python
# tests/ui/test_login_page.py
import pytest
from src.adapters.ui.playwright_page import PlaywrightPage


@pytest.mark.ui
@pytest.mark.asyncio
async def test_user_login():
    """Test user login flow."""
    async with PlaywrightPage("chromium", headless=True) as page:
        await page.goto("https://example.com/login")
        await page.fill("#username", "testuser")
        await page.fill("#password", "testpass")
        await page.click("#login-button")
        
        # Assertions
        await page.wait_for_selector("#dashboard")
        assert await page.is_visible("#welcome-message")
```

### Performance Testing Example

```python
# tests/performance/test_load_test.py
import pytest
from src.adapters.performance.performance_client import PerformanceClient


@pytest.mark.performance
@pytest.mark.asyncio
async def test_api_load_testing():
    """Test API load with multiple users."""
    client = PerformanceClient(base_url="https://jsonplaceholder.typicode.com")
    
    # Load test with 100 users for 30 seconds
    result = await client.load_test(
        endpoint="/users",
        num_users=100,
        duration_seconds=30
    )
    
    assert result.total_requests > 0
    assert result.p95_response_time < 1000  # P95 under 1 second
    assert result.error_rate < 0.05  # Error rate under 5%
```

### Security Testing Example

```python
# tests/security/test_sql_injection.py
import pytest
from src.adapters.security.security_client import SecurityClient
from src.adapters.security.sql_injection_tester import SQLInjectionTester


@pytest.mark.security
@pytest.mark.asyncio
async def test_sql_injection_protection():
    """Test SQL injection protection."""
    client = SecurityClient(base_url="https://example.com/api")
    tester = SQLInjectionTester(client)
    
    # Test with common SQL injection payloads
    results = await tester.test_endpoint(
        endpoint="/users",
        payload_param="id",
        payloads=["' OR '1'='1", "1; DROP TABLE users--"]
    )
    
    assert all(not r.vulnerable for r in results), "SQL injection vulnerabilities detected"
```

### Database Testing Example

```python
# tests/database/test_data_integrity.py
import pytest
from src.adapters.database.database_client import DatabaseClient
from src.adapters.database.data_integrity_tester import DataIntegrityTester


@pytest.mark.database
async def test_data_integrity():
    """Test database data integrity constraints."""
    client = DatabaseClient(connection_string="sqlite:///test.db")
    tester = DataIntegrityTester(client)
    
    # Test primary key constraint
    pk_result = await tester.test_primary_key(
        table="users",
        pk_column="id"
    )
    assert pk_result.passed, "Primary key constraint violated"
    
    # Test unique constraint
    unique_result = await tester.test_unique_constraint(
        table="users",
        columns=["email"]
    )
    assert unique_result.passed, "Unique constraint violated"
```

### Configuration Example

```yaml
# config/qa.yaml
test:
  environment: staging
  parallel_workers: 4
  timeout: 30
  retry_failed: 2

api:
  base_url: https://api.example.com
  auth:
    type: bearer
    token: ${API_TOKEN}

ui:
  browser: chromium
  headless: true
  viewport: 1920x1080

reporting:
  allure: true
  html: true
  screenshots: on_failure
```

---

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Types
```bash
# API tests only
pytest tests/api/ -m api

# UI tests only
pytest tests/ui/ -m ui

# Integration tests only
pytest tests/integration/ -m integration
```

### Parallel Execution

QA-FRAMEWORK uses **pytest-xdist** for parallel test execution, significantly reducing test suite runtime.

```bash
# Auto-detect number of CPU cores
pytest -n auto

# Use specific number of workers
pytest -n 4

# Use logical CPU count
pytest -n logical

# Distribute tests by scope (group related tests)
pytest -n 4 --dist=loadscope

# Distribute tests by file
pytest -n 4 --dist=loadfile

# Run with coverage in parallel
pytest -n 4 --cov=src --cov-report=html
```

#### Parallel Test Configuration

Configure parallel execution in `config/qa.yaml`:

```yaml
test:
  parallel_workers: 4  # Default number of workers
  timeout: 30
```

#### Parallel Test Markers

Use markers to control parallel execution:

```python
import pytest

@pytest.mark.parallel_safe  # Safe to run in parallel (default)
def test_safe_in_parallel():
    """This test can run concurrently with others."""
    assert True

@pytest.mark.serial  # Run serially, not in parallel
def test_must_run_serially():
    """This test runs alone without parallelization."""
    assert True

@pytest.mark.isolated  # Complete isolation from other tests
def test_requires_isolation():
    """This test has complete resource isolation."""
    assert True
```

#### Parallel Fixtures

The framework provides thread-safe fixtures for parallel execution:

```python
import pytest
from typing import Dict, Any

# Worker identification
def test_worker_info(worker_id: str, session_id: str):
    """Access worker and session identifiers."""
    assert worker_id.startswith("gw") or worker_id == "master"
    assert len(session_id) == 8

# Thread-safe locks
def test_with_synchronization(resource_lock):
    """Use locks for thread-safe operations."""
    with resource_lock:
        # Critical section - only one test at a time
        modify_shared_resource()

# Isolated test data
def test_data_isolation(isolated_test_data: Dict[str, Any]):
    """Each test gets isolated data storage."""
    isolated_test_data["key"] = "value"
    assert isolated_test_data["key"] == "value"

# Worker-scoped resources
def test_worker_resources(worker_resource_pool: Dict[str, Any]):
    """Access worker-scoped resource pool."""
    worker_resource_pool["counter"] = worker_resource_pool.get("counter", 0) + 1
    assert worker_resource_pool["counter"] >= 1

# Execution context
def test_execution_context(execution_context: Dict[str, Any]):
    """Access execution metadata."""
    assert "worker_id" in execution_context
    assert "process_id" in execution_context
    assert "thread_id" in execution_context
```

#### Parallel Test Examples

Run parallel examples:

```bash
# Basic parallel tests
pytest tests/unit/test_parallel_basic.py -n 4 -v

# Tests with isolation
pytest tests/unit/test_parallel_isolation.py -n 4 -v

# Resource sharing tests
pytest tests/unit/test_parallel_resources.py -n 4 -v

# Performance benchmarks
pytest tests/unit/test_parallel_performance.py -n 4 -v

# Run only serial tests
pytest tests/unit/test_parallel_isolation.py -m serial -v
```

#### Parallel Test Best Practices

1. **Use `@pytest.mark.parallel_safe`** for tests that can run concurrently
2. **Use `@pytest.mark.serial`** for tests requiring exclusive access
3. **Use `isolated_test_data`** fixture for test-specific data
4. **Use `resource_lock`** for thread-safe access to shared resources
5. **Avoid global state** - use fixtures for state management
6. **Keep tests independent** - no dependencies between tests
7. **Use worker-scoped fixtures** for expensive resources (databases, browsers)

### With Coverage
```bash
pytest --cov=src --cov-report=html
```

### With Allure Reporting
```bash
pytest --alluredir=allure-results
allure serve allure-results
```

---

## 📊 SOLID Principles Implementation

### Single Responsibility (S)
Each class has one reason to change. Example:
```python
# ✅ GOOD - One responsibility
class HTTPClient:
    def get(self, url): ...
    def post(self, url, data): ...

# ❌ BAD - Multiple responsibilities
class HTTPClient:
    def get(self, url): ...
    def post(self, url, data): ...
    def save_to_database(self, data): ...
    def send_email_notification(self): ...
```

### Open/Closed (O)
Open for extension, closed for modification:
```python
class TestReporter:
    def report(self, result: TestResult):
        # Can be extended with new reporters
        pass

class HTMLReporter(TestReporter):
    def report(self, result: TestResult):
        # HTML reporting implementation
        pass

class AllureReporter(TestReporter):
    def report(self, result: TestResult):
        # Allure reporting implementation
        pass
```

---

## 🔧 Configuration

The framework supports multiple configuration sources:

1. **YAML files** - `config/qa.yaml`
2. **JSON files** - `config/qa.json`
3. **Environment variables** - `.env` file
4. **Command line arguments**

Configuration priority: CLI args > ENV > YAML/JSON

---

## 📦 Dependencies

### Core
- **pytest** - Testing framework
- **httpx** - Async HTTP client
- **playwright** - Browser automation
- **pydantic** - Data validation
- **pyyaml** - YAML configuration

### Development
- **black** - Code formatter
- **ruff** - Fast Python linter
- **mypy** - Static type checker
- **pre-commit** - Git hooks

### Optional
- **selenium** - Alternative browser automation
- **locust** - Performance testing
- **bandit** - Security testing
- **safety** - Dependency security

---

## 🐳 Docker Support

```bash
# Build Docker image
docker build -t qa-framework .

# Run tests in Docker
docker run qa-framework pytest

# With docker-compose
docker-compose up
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Use **Black** for formatting
- Follow **PEP 8** guidelines
- Add **type hints** (100%)
- Write **docstrings** (Google style)
- Add **tests** for new features

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Alfred** - Initial work

---

## 🙏 Acknowledgments

- Clean Architecture principles by Robert C. Martin
- SOLID principles inspiration
- Pytest community
- Playwright team

---

<p align="center">
  <strong>⭐ Star this repo if it helped you! ⭐</strong>
</p>

<p align="center">
  Built with ❤️ by <a href="https://github.com/alfred">Alfred</a>
</p>
