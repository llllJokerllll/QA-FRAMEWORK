# Structured Logging Documentation

## Overview

QA-Framework Dashboard uses **structlog** for structured logging with support for both console (development) and JSON (production) output formats. This provides comprehensive logging with context binding, request tracing, and consistent formatting across all services.

## Features

- **JSON structured logging** for production environments
- **Console colored logging** for development environments
- **Request ID tracing** - Every request gets a unique ID automatically tracked through the context
- **Context binding** - Add custom context to all subsequent log entries
- **Automatic timestamps** - ISO 8601 format with UTC timezone
- **Log level filtering** - Configurable via environment variables

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `ENVIRONMENT` | Environment name (development, production, staging) | `development` |

### Output Formats

The logging format is automatically selected based on the `ENVIRONMENT` variable:

- **Development** (`development`, `dev`): Console output with colors
- **Production** (`production`, `prod`, `staging`): JSON output for log aggregation

### Manual Configuration

```python
from core.logging_config import configure_logging

# Configure with automatic format detection
configure_logging(log_level="DEBUG")

# Or specify format explicitly
configure_logging(log_level="INFO", json_format=True)
```

## Usage

### Basic Logging

```python
from core.logging_config import get_logger

# Get a logger
logger = get_logger(__name__)

# Log messages with structured data
logger.info("User action", user_id=123, action="login")
logger.debug("Processing data", data_size=1024, format="json")
logger.warning("Resource low", memory_percent=85, cpu_percent=92)
logger.error("Operation failed", error_code=500, details="Connection timeout")
```

### Request ID Tracing

Every HTTP request automatically gets a unique `request_id` that is included in all logs for that request:

```python
# Set request ID manually (if needed)
from core.logging_config import set_request_id, clear_request_id

set_request_id("abc-123")
logger.info("Processing request")  # Will include request_id

clear_request_id()  # Clear when done
```

### Context Binding

Bind context that will be included in all subsequent logs:

```python
import structlog

with structlog.contextvars.bound_contextvars(user_id=123, session_id="xyz"):
    logger.info("Action 1")  # Includes user_id and session_id
    logger.info("Action 2")  # Also includes user_id and session_id

# Outside the context, they're gone
logger.info("Action 3")  # No user_id or session_id
```

## Log Structure

### Console Output (Development)

```
2024-01-15T10:30:45.123456Z [INFO] backend.services.auth_service: User authenticated successfully username=john_doe user_id=42
2024-01-15T10:30:45.234567Z [DEBUG] backend.api.v1.routes: Request completed method=GET url=/api/v1/dashboard/stats status_code=200 duration_ms=45.67
```

### JSON Output (Production)

```json
{
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "level": "info",
  "logger": "backend.services.auth_service",
  "event": "User authenticated successfully",
  "username": "john_doe",
  "user_id": 42,
  "request_id": "abc-123-xyz"
}
```

## Services with Logging

All critical services include comprehensive logging:

### Authentication Service (`services/auth_service.py`)
- Login attempts (success/failure)
- Token validation
- Password hashing operations
- Authentication errors

### Suite Service (`services/suite_service.py`)
- Suite creation, updates, and deletions
- Listing operations with counts
- Retrieval by ID
- Error cases

### Case Service (`services/case_service.py`)
- Test case CRUD operations
- Validation failures
- Suite association checks

### Execution Service (`services/execution_service.py`)
- Execution creation and management
- Test run progress
- Completion summaries
- Error tracking

### User Service (`services/user_service.py`)
- User registration and updates
- Duplicate checks
- Soft delete operations

## API Routes Logging

The API layer includes a middleware that automatically logs:

- **Request start**: Method, URL, client IP, request_id
- **Request completion**: Status code, duration
- **Errors**: Full error details with stack traces

Example:
```python
# All routes automatically get request logging
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    logger.info("Getting user", user_id=user_id)  # Includes request_id automatically
    # ... logic
    logger.info("User retrieved successfully", user_id=user_id)
```

## Best Practices

1. **Use descriptive event names**: `"User authentication failed"` not `"Error"`
2. **Include relevant IDs**: Always include `user_id`, `suite_id`, `case_id`, etc.
3. **Log at appropriate levels**:
   - `DEBUG`: Detailed debugging info
   - `INFO`: Normal operations
   - `WARNING`: Suspicious but handled
   - `ERROR`: Failures requiring attention
4. **Use structured data**: `logger.info("Login", user_id=123)` not `logger.info(f"User {user_id} logged in")`
5. **Include request_id**: Always available via context in API routes

## Example Usage in Services

```python
from core.logging_config import get_logger

logger = get_logger(__name__)

async def create_suite_service(suite_data: TestSuiteCreate, user_id: int, db: AsyncSession):
    logger.info("Creating new test suite", 
                name=suite_data.name, 
                framework_type=suite_data.framework_type,
                user_id=user_id)
    
    try:
        # ... logic ...
        logger.info("Test suite created successfully", 
                    suite_id=db_suite.id,
                    name=db_suite.name)
        return db_suite
    except Exception as e:
        logger.error("Failed to create test suite", 
                     error=str(e),
                     exc_info=True)
        raise
```

## Troubleshooting

### Logs not appearing
- Check `LOG_LEVEL` environment variable
- Ensure `configure_logging()` is called at application startup
- Verify the logger name matches your module path

### Missing request_id
- The middleware must be registered in the FastAPI app
- Ensure routes are using the provided router with middleware

### Too verbose logs
- Increase log level: `LOG_LEVEL=WARNING`
- Third-party library logs are automatically reduced (uvicorn, sqlalchemy, asyncio)

## Integration with Log Aggregation

For production deployments, the JSON format is compatible with:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Splunk
- Datadog
- CloudWatch Logs
- Fluentd/Fluent Bit

Simply pipe stdout to your log collector:
```bash
python -m uvicorn main:app --log-level warning 2>&1 | fluent-bit -i stdin -o elasticsearch
```
