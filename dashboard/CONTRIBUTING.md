# Contributing to QA-FRAMEWORK Dashboard

Thank you for your interest in contributing to the QA-FRAMEWORK Dashboard! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker and Docker Compose

### Setup Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/qa-framework-dashboard.git
   cd qa-framework-dashboard
   ```

2. **Run Setup Script**
   ```bash
   ./setup.sh
   ```

3. **Start Development Environment**
   ```bash
   docker-compose up -d
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming convention:
- `feature/` for new features
- `bugfix/` for bug fixes
- `hotfix/` for critical fixes
- `docs/` for documentation

### 2. Make Changes

- Write clean, readable code
- Follow coding standards
- Add tests for new functionality
- Update documentation

### 3. Test Your Changes

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=backend

# Frontend tests
cd frontend
npm run test
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

## Coding Standards

### Python (Backend)

- **Style Guide**: PEP 8
- **Formatter**: Black
- **Linter**: Flake8
- **Type Hints**: Required for all functions
- **Docstrings**: Google style

```python
def example_function(param1: str, param2: int) -> dict:
    """
    Example function with proper documentation.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Dictionary with results
    
    Raises:
        ValueError: If parameters are invalid
    """
    # Implementation
    return {"result": "value"}
```

### TypeScript (Frontend)

- **Style Guide**: Airbnb
- **Formatter**: Prettier
- **Linter**: ESLint
- **TypeScript**: Strict mode enabled

```typescript
interface ExampleProps {
  title: string;
  count: number;
}

export const ExampleComponent: React.FC<ExampleProps> = ({ title, count }) => {
  // Implementation
  return <div>{title}: {count}</div>;
};
```

### General Principles

- **SOLID Principles**: Follow SOLID design principles
- **Clean Architecture**: Maintain separation of concerns
- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It

## Testing Guidelines

### Test Requirements

- **Unit Tests**: Required for all services
- **Integration Tests**: Required for API endpoints
- **E2E Tests**: Required for critical user flows
- **Coverage**: Minimum 80% coverage

### Test Structure

```python
@pytest.mark.asyncio
class TestYourFeature:
    """Test suite for your feature"""
    
    async def test_success_case(self):
        """Test successful operation"""
        # Arrange
        # Act
        # Assert
        pass
    
    async def test_error_case(self):
        """Test error handling"""
        # Test error scenarios
        pass
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_file.py

# With coverage
pytest --cov=backend --cov-report=html

# Verbose output
pytest -v -s
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

### Examples

```
feat(auth): add JWT refresh token support

- Implement refresh token generation
- Add token rotation mechanism
- Update auth service tests

Closes #123
```

```
fix(api): correct rate limiting for login endpoint

Fixes issue where rate limiting was not properly applied to login attempts.
Now correctly limits to 5 attempts per minute.

Fixes #456
```

## Pull Request Process

### 1. PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows coding standards
- [ ] All tests pass
- [ ] Coverage is maintained or improved
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] No sensitive data in commits

### 2. PR Template

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
- [ ] All tests pass

## Checklist
- [ ] Code follows standards
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG updated
```

### 3. Review Process

1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: At least one approval required
3. **Testing**: All tests must pass
4. **Merge**: Squash and merge to main

### 4. After Merge

- Delete feature branch
- Update local main branch
- Start new feature/bugfix

## Documentation

### When to Update

- New features or endpoints
- API changes
- Configuration changes
- Breaking changes

### What to Update

- README.md
- CHANGELOG.md
- API documentation
- Code comments and docstrings

## Getting Help

- **Issues**: Create an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers directly

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

---

Thank you for contributing to QA-FRAMEWORK Dashboard! 🚀

**Maintained by:** Alfred - Senior Project Manager & Lead Developer