# QA-FRAMEWORK Dashboard - Testing Guide

This document provides comprehensive information about testing the QA-FRAMEWORK Dashboard.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)

## Overview

The QA-FRAMEWORK Dashboard uses a multi-level testing strategy:

1. **Unit Tests**: Test individual functions and services
2. **Integration Tests**: Test API endpoints and database interactions
3. **E2E Tests**: Test complete user flows with Playwright
4. **Performance Tests**: Load testing and benchmarking

## Test Structure

```
backend/
├── tests/
│   ├── unit/              # Unit tests
│   │   ├── test_auth_service.py
│   │   ├── test_suite_service.py
│   │   ├── test_case_service.py (TODO)
│   │   └── test_execution_service.py (TODO)
│   ├── integration/       # Integration tests (TODO)
│   │   ├── test_api.py
│   │   └── test_db.py
│   └── conftest.py        # Pytest fixtures
├── pytest.ini            # Pytest configuration
└── requirements.txt      # Test dependencies

frontend/
├── src/
│   └── __tests__/        # Component tests (TODO)
└── e2e/                  # E2E tests (TODO)
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### Run All Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=backend --cov-report=html

# Run specific test file
pytest tests/unit/test_auth_service.py -v

# Run specific test
pytest tests/unit/test_auth_service.py::TestAuthService::test_hash_password -v
```

### Run by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests (when available)
pytest -m integration

# Run slow tests
pytest -m slow
```

### Run with Different Verbosity

```bash
# Minimal output
pytest tests/unit/

# Verbose output
pytest tests/unit/ -v

# Very verbose (including print statements)
pytest tests/unit/ -vv -s
```

## Test Coverage

### Coverage Goals

- **Minimum**: 80%
- **Target**: 90%
- **Critical Services**: 95% (auth, execution)

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=backend --cov-report=term-missing

# HTML report
pytest --cov=backend --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest --cov=backend --cov-report=xml
```

### Current Coverage

- **Auth Service**: ~95%
- **Suite Service**: ~90%
- **Case Service**: N/A (TODO)
- **Execution Service**: N/A (TODO)
- **Dashboard Service**: N/A (TODO)

## Writing Tests

### Unit Test Template

```python
import pytest
from unittest.mock import AsyncMock, Mock

@pytest.mark.asyncio
class TestYourService:
    """Test suite for your service"""
    
    async def test_function_success(self):
        """Test successful operation"""
        # Arrange
        mock_db = AsyncMock()
        
        # Act
        result = await your_function(mock_db)
        
        # Assert
        assert result is not None
    
    async def test_function_failure(self):
        """Test failure case"""
        # Arrange
        mock_db = AsyncMock()
        
        # Act & Assert
        with pytest.raises(Exception):
            await your_function(mock_db)
```

### Integration Test Template

```python
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

def test_endpoint_success(client):
    """Test endpoint with valid data"""
    response = client.post("/api/v1/endpoint", json={"key": "value"})
    assert response.status_code == 200
    assert response.json()["success"] is True
```

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`
- Use descriptive names: `test_create_user_with_valid_data`

### What to Test

1. **Happy Path**: Normal successful operations
2. **Error Cases**: Invalid inputs, exceptions
3. **Edge Cases**: Boundary conditions, empty inputs
4. **Security**: Authentication, authorization
5. **Performance**: Response times, resource usage

## CI/CD Integration

### GitHub Actions (Planned)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Test Best Practices

### 1. Isolation
- Each test should be independent
- Use fixtures for common setup
- Clean up after tests

### 2. Clarity
- Use descriptive test names
- Add docstrings explaining what's tested
- Keep tests simple and focused

### 3. Speed
- Mock external dependencies
- Use in-memory databases for integration tests
- Parallelize tests when possible

### 4. Maintainability
- DRY (Don't Repeat Yourself)
- Use parametrized tests
- Update tests when code changes

### 5. Coverage
- Aim for high coverage but prioritize quality
- Test critical paths thoroughly
- Don't test trivial code

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the backend directory
   cd backend
   # Ensure virtual environment is activated
   source venv/bin/activate
   ```

2. **Database Errors**
   ```bash
   # Use test database
   export DATABASE_URL=sqlite:///test.db
   pytest tests/
   ```

3. **Async Tests**
   ```python
   # Mark async tests with @pytest.mark.asyncio
   @pytest.mark.asyncio
   async def test_async_function():
       result = await async_operation()
       assert result is not None
   ```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)

## Contact

For questions about testing, contact the development team or create an issue in the repository.

---

**Last Updated:** 2026-02-12  
**Maintained by:** Alfred - Senior Project Manager & Lead Developer