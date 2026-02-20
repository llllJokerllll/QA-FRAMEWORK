"""
OpenAPI Configuration for QA-Framework API
Enhanced documentation with examples and descriptions
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def create_openapi_schema(app: FastAPI) -> dict:
    """
    Create enhanced OpenAPI schema with detailed examples.
    
    Returns:
        dict: OpenAPI schema with comprehensive documentation
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="QA-Framework API",
        version="1.0.0",
        description="""
## QA-Framework API Documentation

This API provides comprehensive test management and execution capabilities.

### Features:
- **Test Management**: Create, update, delete test suites and cases
- **Test Execution**: Run tests and track results
- **Reporting**: Generate HTML, JSON, and XML reports
- **Integrations**: Connect with Jira, Zephyr, Azure DevOps
- **Dashboard**: Real-time monitoring and analytics

### Authentication:
All API endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-token>
```

### Rate Limiting:
- Read operations: 200 requests/minute
- Write operations: 50 requests/minute
- Execution operations: 10 requests/minute
        """,
        routes=app.routes,
    )
    
    # Add comprehensive examples
    openapi_schema["info"]["contact"] = {
        "name": "QA-Framework Support",
        "email": "support@qa-framework.com",
        "url": "https://github.com/llllJokerllll/QA-FRAMEWORK"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    # Add example values to paths
    if "/api/v1/suites" in openapi_schema["paths"]:
        suite_path = openapi_schema["paths"]["/api/v1/suites"]
        
        # POST example
        if "post" in suite_path:
            suite_path["post"]["requestBody"]["content"]["application/json"]["example"] = {
                "name": "Login Tests",
                "description": "Comprehensive login functionality tests",
                "tags": ["authentication", "smoke"],
                "priority": "high"
            }
            suite_path["post"]["responses"]["201"]["description"] = "Suite created successfully"
            suite_path["post"]["responses"]["201"]["content"] = {
                "application/json": {
                    "example": {
                        "id": "suite_123",
                        "name": "Login Tests",
                        "description": "Comprehensive login functionality tests",
                        "created_at": "2026-02-20T10:00:00Z",
                        "test_count": 0,
                        "status": "active"
                    }
                }
            }
    
    app.openapi_schema = openapi_schema
    return openapi_schema
