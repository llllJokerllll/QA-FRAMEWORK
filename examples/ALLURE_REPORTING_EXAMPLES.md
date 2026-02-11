# Allure Reporting System - Examples of Usage

**Autor:** Alfred  
**Fecha:** 2026-02-11 19:50 UTC

---

## 📊 Overview

The Reporting System in QA-FRAMEWORK includes:
- **Allure Reporter** - Advanced XML reports
- **HTML Reporter** - HTML reports with CSS
- **JSON Reporter** - Machine-readable JSON reports

---

## 🚀 Quick Start Examples

### Example 1: Basic API Testing with Reporting

```python
# examples/basic_api_reporting_example.py
import pytest
import asyncio
from src.adapters.http.httpx_client import HTTPXClient
from src.core.entities.test_result import TestResult
from src.infrastructure.config.config_manager import ConfigManager
from src.adapters.reporting.allure_reporter import AllureReporter


@pytest.mark.api
@pytest.mark.asyncio
async def test_api_with_allure_reporting():
    """Test API endpoint and generate Allure report"""
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    # Initialize reporter
    reporter = AllureReporter(config)
    
    # Create test client
    client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
    
    # Execute API call
    response = await client.get("/users")
    
    # Generate report
    result = TestResult(
        test_name="test_api_with_allure_reporting",
        status=TestStatus.PASSED if response.status_code == 200 else TestStatus.FAILED,
        execution_time=1.5,
        metadata={
            "endpoint": "/users",
            "response_code": response.status_code,
            "data_size": len(response.json())
        }
    )
    
    reporter.report(result, output_dir="allure-results")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "api"])
```

### Example 2: Run with Allure Report

```bash
# Run tests with Allure reporting
pytest tests/api/ -v --alluredir=allure-results

# Generate Allure HTML report
allure generate allure-results --clean allure-report

# Open Allure report
allure open allure-report
```

### Example 3: Parallel Testing with Reporting

```python
# examples/parallel_reporting_example.py
import pytest
from src.adapters.http.httpx_client import HTTPXClient


@pytest.mark.api
@pytest.mark.parallel_safe
def test_parallel_with_reporting():
    """Test that runs in parallel and generates reports"""
    client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
    response = client.get("/users")
    
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-n", "4", "--alluredir=allure-results"])
```

### Example 4: Generate Reports Manually

```python
# examples/manual_report_generation.py
from src.adapters.reporting.allure_reporter import AllureReporter
from src.core.entities.test_result import TestResult
from src.infrastructure.config.config_manager import ConfigManager


def generate_report():
    """Generate a manual report without running tests"""
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    reporter = AllureReporter(config)
    
    # Create sample test result
    result = TestResult(
        test_name="manual_report_example",
        status=TestStatus.PASSED,
        execution_time=0.0,
        metadata={
            "report_type": "manual",
            "description": "Manually generated report"
        }
    )
    
    # Generate report
    reporter.report(result, output_dir="allure-results")
    print("Allure report generated in allure-results/")


if __name__ == "__main__":
    generate_report()
```

---

## 🎯 Advanced Examples

### Example 5: Multiple Test Scenarios with Reporting

```python
# examples/multiple_scenarios_reporting.py
import pytest
import asyncio
from src.adapters.http.httpx_client import HTTPXClient
from src.adapters.reporting.allure_reporter import AllureReporter


@pytest.mark.api
@pytest.mark.asyncio
async def test_scenario_1_success():
    """Scenario 1: Successful API call"""
    client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
    response = await client.get("/users")
    assert response.status_code == 200


@pytest.mark.api
@pytest.mark.asyncio
async def test_scenario_2_failure():
    """Scenario 2: Failed API call"""
    client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
    response = await client.get("/invalid-endpoint")
    assert response.status_code == 404


@pytest.mark.api
@pytest.mark.asyncio
async def test_scenario_3_slow_operation():
    """Scenario 3: Slow operation"""
    client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
    response = await client.get("/users?_delay=5")
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "-s",
        "-m", "api",
        "--alluredir=allure-results"
        "-k", "scenario"
    ])
```

---

## 📋 Complete Reporting Workflow

### Step 1: Run Tests
```bash
# Run all tests with Allure reporting
pytest -v --alluredir=allure-results tests/
```

### Step 2: Generate HTML Report
```bash
# Generate Allure HTML report
allure generate allure-results --clean allure-report
```

### Step 3: View Report
```bash
# Open report in browser (if on local machine)
allure open allure-report

# Or serve report (if on remote server)
allure serve -p 8080 allure-results
```

---

## 🔧 Configuration

### In config/qa.yaml

```yaml
reporting:
  allure:
    enabled: true
    output_dir: allure-results
    history: true
    trending: true
  
  html:
    enabled: true
    output_dir: html-results
    template: modern
  
  json:
    enabled: true
    output_dir: json-results
```

---

## 📊 Report Types

### Allure Reports

**Features:**
- Interactive HTML reports
- Test history and trends
- Screenshots and attachments
- Filters and search
- Comparison between runs

**Structure:**
```
allure-results/
├── history/
├── trends/
├── widgets/
└── *.xml (test data)
```

### HTML Reports

**Features:**
- Standalone HTML files
- Custom styling
- Embedded charts
- No server required

**Structure:**
```
html-results/
├── index.html (main report)
├── css/
├── js/
└── assets/
```

### JSON Reports

**Features:**
- Machine-readable
- Easy to parse
- Integrates with CI/CD

**Structure:**
```
json-results/
├── report.json
└── data.json
```

---

## 🎯 Best Practices for Reporting

1. **Always use descriptive test names**
   ```python
   async def test_user_api_endpoint_get_all_users_should_return_200():
   ```

2. **Add relevant metadata**
   ```python
   result = TestResult(
       test_name="test_example",
       status=TestStatus.PASSED,
       metadata={
           "api_endpoint": "/users",
           "response_time_ms": 150,
           "environment": "staging"
       }
   )
   ```

3. **Use appropriate report types**
   - Allure for interactive exploration
   - HTML for sharing
   - JSON for automation/CI-CD

4. **Clean old reports**
   ```bash
   # Clean old Allure reports
   allure history clear --before 30d
   ```

5. **Customize report appearance**
   ```bash
   # Allure with custom theme
   allure generate --clean allure-report --report-title "My Test Report"
   ```

---

## 🚀 Integration with CI/CD

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-allure
      - name: Run tests
        run: |
          pytest -v --alluredir=allure-results
      - name: Generate Allure report
        uses: simple-actions/allure-report@v1
        with:
          allure-results: allure-results
          allure-history: allure-history
      - name: Upload Allure report
        uses: actions/upload-artifact@v4
        with:
          name: allure-report
          path: allure-report
```

---

## 📝 Creating Custom Reports

### Custom HTML Report Template

```python
# examples/custom_report_template.py
from src.adapters.reporting.html_reporter import HTMLReporter
from src.infrastructure.config.config_manager import ConfigManager


def create_custom_report(test_results):
    """Create a custom HTML report"""
    config_manager = ConfigManager()
    reporter = HTMLReporter(config)
    
    # Generate report with custom metadata
    for result in test_results:
        reporter.report(result, output_dir="custom-reports")
    
    print("Custom report generated in custom-reports/")


if __name__ == "__main__":
    # Example test results
    from src.core.entities.test_result import TestResult, TestStatus
    
    results = [
        TestResult(f"test_{i}", TestStatus.PASSED, 1.5)
        for i in range(10)
    ]
    
    create_custom_report(results)
```

---

## 🎯 Summary

The QA-FRAMEWORK reporting system provides:

1. ✅ **Allure XML generation** - For interactive exploration
2. ✅ **HTML report generation** - For sharing
3. ✅ **JSON report generation** - For automation
4. ✅ **Multiple reporters** - Easy to use
5. ✅ **Configuration integration** - Works with config system
6. ✅ **Clean Architecture** - SOLID principles applied
7. ✅ **Full examples** - Ready to use

---

**Quick Commands:**
```bash
# Run tests with Allure
pytest tests/ -v --alluredir=allure-results

# Generate report
allure generate allure-results --clean allure-report

# View report
allure open allure-report

# Generate custom report
python examples/manual_report_generation.py
```

---

**Created:** 2026-02-11 19:50 UTC  
**Author:** Alfred
