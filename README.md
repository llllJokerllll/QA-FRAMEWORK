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
- 🧪 **Multi-Type Testing** - API, UI, Integration, E2E, Performance, Security
- 🚀 **Async Support** - Full async/await support with HTTPX and Playwright
- 📊 **Advanced Reporting** - Allure, HTML, JSON reports with screenshots/videos
- ⚡ **Parallel Execution** - pytest-xdist for faster test runs
- 🔧 **Flexible Configuration** - YAML/JSON/ENV configuration support
- 🧱 **Type Safety** - 100% type hints with Pydantic
- 📝 **Comprehensive Documentation** - Docstrings and examples
- 🔄 **CI/CD Ready** - GitHub Actions and Docker support

---

## 🎯 Supported Testing Types

| Type | Tools | Status |
|------|-------|--------|
| **API Testing** | HTTPX, Requests | ✅ Supported |
| **UI Testing** | Playwright | ✅ Supported |
| **Integration Testing** | Pytest | ✅ Supported |
| **E2E Testing** | Playwright | ✅ Supported |
| **Performance Testing** | Locust | 🔄 Planned |
| **Security Testing** | Bandit, Safety | 🔄 Planned |

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
│   │   ├── performance/       # Locust
│   │   └── security/          # Bandit, Safety
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
```bash
# Use all available CPU cores
pytest -n auto

# Use specific number of workers
pytest -n 4
```

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
