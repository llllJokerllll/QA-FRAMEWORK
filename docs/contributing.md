# Contributing to QA-Framework

Thank you for your interest in contributing to QA-Framework! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all.

### Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what is best for the community
- Show empathy towards others

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Git
- Docker (optional)

### Setup Development Environment

1. **Fork and Clone**

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/QA-FRAMEWORK.git
cd QA-FRAMEWORK

# Add upstream remote
git remote add upstream https://github.com/llllJokerllll/QA-FRAMEWORK.git
```

2. **Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. **Set Up Pre-commit Hooks**

```bash
pip install pre-commit
pre-commit install
```

5. **Run Tests**

```bash
pytest
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/my-fix
# or
git checkout -b docs/my-docs
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements
- `chore/` - Maintenance tasks

### 2. Make Changes

Write clean, well-documented code following our coding standards.

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/unit/test_module.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### 4. Commit Changes

Follow our commit guidelines (see below).

### 5. Push Changes

```bash
git push origin feature/my-feature
```

### 6. Create Pull Request

Open a pull request on GitHub.

## Coding Standards

### Python

We follow PEP 8 with some modifications:

**Formatting:**
- Line length: 100 characters
- Use 4 spaces for indentation
- Use double quotes for strings

**Linting:**
```bash
# Run Black
black src tests

# Run Ruff
ruff check src tests

# Run MyPy
mypy src
```

**Type Hints:**
```python
# Good
def calculate_total(items: list[dict[str, Any]]) -> float:
    ...

# Bad
def calculate_total(items):
    ...
```

**Imports:**
```python
# Standard library
import os
from typing import Optional

# Third-party
import pytest
from fastapi import FastAPI

# Local
from src.domain.entities import TestSuite
from src.application.services import TestService
```

### JavaScript/TypeScript

We follow Airbnb style guide with some modifications:

**Formatting:**
```bash
# Run ESLint
npm run lint

# Run Prettier
npm run format
```

### Documentation

**Docstrings:**
```python
def run_tests(suite_id: str, environment: str) -> ExecutionResult:
    """
    Execute all tests in a test suite.
    
    Args:
        suite_id: Unique identifier for the test suite
        environment: Target environment (dev, staging, prod)
        
    Returns:
        ExecutionResult object with test results
        
    Raises:
        SuiteNotFoundError: If suite_id doesn't exist
        ExecutionError: If test execution fails
        
    Example:
        >>> result = run_tests("suite_123", "staging")
        >>> print(result.passed)
        True
    """
    ...
```

**Comments:**
```python
# Good - Explains why
# Use exponential backoff to avoid overwhelming the server
time.sleep(min(2 ** attempt, 60))

# Bad - Explains what (obvious)
# Sleep for some time
time.sleep(10)
```

## Commit Guidelines

We follow Conventional Commits:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding/updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `style`: Code style changes (formatting, etc.)

### Examples

```bash
# Feature
feat(api): add endpoint for bulk test execution

# Bug fix
fix(auth): correct JWT token validation

# Documentation
docs(readme): update installation instructions

# Breaking change
feat(api)!: change authentication flow

BREAKING CHANGE: The /auth/login endpoint now requires
email instead of username.
```

### Commit Message Guidelines

1. **Subject line:**
   - Use imperative mood ("add feature" not "added feature")
   - Don't end with a period
   - Max 72 characters

2. **Body:**
   - Explain what and why, not how
   - Use bullet points for multiple changes
   - Wrap at 72 characters

3. **Footer:**
   - Reference issues: `Closes #123`
   - Breaking changes: `BREAKING CHANGE: description`

## Pull Request Process

### Before Submitting

- [ ] Code follows coding standards
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages follow guidelines
- [ ] Branch is up-to-date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests pass locally
- [ ] New and existing tests pass

## Related Issues
Closes #123
```

### Review Process

1. **Automated Checks**
   - CI pipeline runs
   - Code quality checks
   - Test coverage

2. **Code Review**
   - At least one approval required
   - All comments addressed
   - No unresolved discussions

3. **Merge**
   - Squash and merge (default)
   - Commit message follows guidelines

## Testing

### Unit Tests

```python
# tests/unit/test_example.py
import pytest
from src.module import function

def test_function_returns_expected_value():
    # Arrange
    input_value = "test"
    expected = "expected"
    
    # Act
    result = function(input_value)
    
    # Assert
    assert result == expected

def test_function_raises_error_on_invalid_input():
    with pytest.raises(ValueError):
        function(None)
```

### Integration Tests

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.presentation.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_create_suite(client):
    response = client.post(
        "/api/v1/suites",
        json={"name": "Test Suite"},
        headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 201
```

### Test Coverage

We aim for:
- **Unit tests:** 80%+ coverage
- **Integration tests:** Critical paths covered
- **E2E tests:** Happy paths covered

Run coverage:
```bash
pytest --cov=src --cov-report=html --cov-fail-under=80
```

## Documentation

### Types of Documentation

1. **Code Documentation**
   - Docstrings
   - Comments for complex logic

2. **API Documentation**
   - OpenAPI/Swagger
   - Example requests/responses

3. **User Documentation**
   - Getting Started
   - Tutorials
   - FAQs

4. **Architecture Documentation**
   - Design decisions
   - System diagrams

### Building Documentation

```bash
cd docs
mkdocs serve
# Open http://localhost:8000
```

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Screenshots
If applicable

## Environment
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11.5]
- QA-Framework version: [e.g., 1.0.0]

## Additional Context
Any other context
```

### Feature Requests

Use the feature request template:

```markdown
## Problem Statement
Clear description of the problem

## Proposed Solution
Describe the feature you'd like

## Alternatives Considered
Other solutions you've considered

## Additional Context
Any other context or screenshots
```

## Getting Help

- **GitHub Issues:** For bug reports and feature requests
- **GitHub Discussions:** For questions and discussions
- **Email:** support@qa-framework.com

## Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project README

Thank you for contributing! 🎉
