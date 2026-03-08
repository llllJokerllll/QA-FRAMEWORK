# 📖 API Reference - QA-FRAMEWORK

Complete REST API documentation for QA-FRAMEWORK.

## 🔑 Authentication

All API requests require authentication via JWT token.

### Getting a Token

```bash
# Login with email/password
curl -X POST https://qa-framework-backend.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Using the Token

```bash
curl -X GET https://qa-framework-backend.railway.app/api/v1/suites \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📋 Test Suites

### List All Suites

```http
GET /api/v1/suites
```

**Response:**
```json
{
  "suites": [
    {
      "id": "uuid",
      "name": "Login Tests",
      "description": "Authentication test suite",
      "test_count": 15,
      "created_at": "2026-02-26T00:00:00Z",
      "updated_at": "2026-02-26T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

### Create Suite

```http
POST /api/v1/suites
```

**Request Body:**
```json
{
  "name": "My Test Suite",
  "description": "Description of the suite",
  "tags": ["smoke", "regression"]
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "My Test Suite",
  "description": "Description of the suite",
  "tags": ["smoke", "regression"],
  "test_count": 0,
  "created_at": "2026-02-26T00:00:00Z"
}
```

### Get Suite

```http
GET /api/v1/suites/{suite_id}
```

### Update Suite

```http
PUT /api/v1/suites/{suite_id}
```

### Delete Suite

```http
DELETE /api/v1/suites/{suite_id}
```

## 🧪 Test Cases

### List Test Cases

```http
GET /api/v1/suites/{suite_id}/cases
```

### Create Test Case

```http
POST /api/v1/suites/{suite_id}/cases
```

**Request Body:**
```json
{
  "name": "Test user login",
  "description": "Verify user can log in with valid credentials",
  "steps": [
    "Navigate to login page",
    "Enter email",
    "Enter password",
    "Click login button",
    "Verify dashboard is displayed"
  ],
  "expected_result": "User is redirected to dashboard",
  "priority": "high",
  "tags": ["authentication", "smoke"]
}
```

### Get Test Case

```http
GET /api/v1/cases/{case_id}
```

### Update Test Case

```http
PUT /api/v1/cases/{case_id}
```

### Delete Test Case

```http
DELETE /api/v1/cases/{case_id}
```

## 🚀 Executions

### Run Suite

```http
POST /api/v1/suites/{suite_id}/run
```

**Response:**
```json
{
  "execution_id": "uuid",
  "suite_id": "uuid",
  "status": "running",
  "started_at": "2026-02-26T00:00:00Z"
}
```

### Get Execution Status

```http
GET /api/v1/executions/{execution_id}
```

**Response:**
```json
{
  "id": "uuid",
  "suite_id": "uuid",
  "status": "completed",
  "total_tests": 15,
  "passed": 13,
  "failed": 2,
  "skipped": 0,
  "started_at": "2026-02-26T00:00:00Z",
  "completed_at": "2026-02-26T00:05:00Z",
  "duration_seconds": 300
}
```

### List Executions

```http
GET /api/v1/executions
```

**Query Parameters:**
- `suite_id` (optional): Filter by suite
- `status` (optional): Filter by status (running, completed, failed)
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)

## 🤖 AI Features

### Self-Healing

#### Get Healing Sessions

```http
GET /api/v1/healing/sessions
```

#### Trigger Manual Healing

```http
POST /api/v1/healing/heal
```

**Request Body:**
```json
{
  "selector_id": "uuid",
  "force": false
}
```

### AI Test Generation

#### Generate from Requirements

```http
POST /api/v1/ai/generate/from-requirements
```

**Request Body:**
```json
{
  "requirements": "Feature: User login\n  As a user\n  I want to log in\n  So that I can access my account",
  "format": "gherkin",
  "framework": "playwright"
}
```

**Response:**
```json
{
  "tests": [
    {
      "name": "test_successful_login",
      "code": "import { test, expect } from '@playwright/test';\n...",
      "confidence": 0.95
    }
  ],
  "scenarios": 3,
  "edge_cases": 5
}
```

#### Generate from UI

```http
POST /api/v1/ai/generate/from-ui
```

**Request Body:**
```json
{
  "url": "https://example.com",
  "actions": [
    {"type": "click", "selector": "#login-button"},
    {"type": "fill", "selector": "#email", "value": "test@example.com"}
  ]
}
```

### Flaky Detection

#### Get Flaky Tests

```http
GET /api/v1/flaky/tests
```

**Response:**
```json
{
  "tests": [
    {
      "id": "uuid",
      "name": "Test payment processing",
      "flakiness_score": 0.75,
      "quarantine_status": "active",
      "last_passed": "2026-02-25T00:00:00Z",
      "last_failed": "2026-02-26T00:00:00Z",
      "failure_rate": 0.3
    }
  ]
}
```

#### Get Root Cause Analysis

```http
GET /api/v1/flaky/tests/{test_id}/analysis
```

## 💳 Billing

### Get Subscription

```http
GET /api/v1/billing/subscription
```

### Create Checkout Session

```http
POST /api/v1/billing/checkout
```

**Request Body:**
```json
{
  "price_id": "price_pro_monthly",
  "success_url": "https://app.qa-framework.io/success",
  "cancel_url": "https://app.qa-framework.io/cancel"
}
```

### Cancel Subscription

```http
POST /api/v1/billing/cancel
```

### Get Usage

```http
GET /api/v1/billing/usage
```

**Response:**
```json
{
  "period_start": "2026-02-01T00:00:00Z",
  "period_end": "2026-02-28T23:59:59Z",
  "test_executions": {
    "used": 45000,
    "limit": 50000,
    "percentage": 90
  },
  "ai_healings": {
    "used": 120,
    "limit": 500,
    "percentage": 24
  }
}
```

## 📊 Reports

### Generate HTML Report

```http
GET /api/v1/executions/{execution_id}/report/html
```

### Generate JSON Report

```http
GET /api/v1/executions/{execution_id}/report/json
```

## 🔍 Health Check

### API Health

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-26T00:00:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "ai": "healthy"
  }
}
```

## 🚦 Rate Limits

| Plan | Requests/min | Executions/month |
|------|--------------|------------------|
| Free | 60 | 1,000 |
| Pro | 300 | 50,000 |
| Enterprise | Unlimited | Unlimited |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1708905600
```

## 🔄 Pagination

All list endpoints support pagination:

```http
GET /api/v1/suites?page=2&per_page=50
```

**Response includes:**
```json
{
  "total": 150,
  "page": 2,
  "per_page": 50,
  "total_pages": 3
}
```

## ❌ Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Invalid input data |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## 📝 SDK Examples

### Python

```python
from qaframework import Client

client = Client(api_key="your-api-key")

# Create suite
suite = client.suites.create(
    name="My Suite",
    description="Test suite"
)

# Run suite
execution = client.suites.run(suite.id)

# Check status
status = client.executions.get(execution.id)
print(f"Status: {status.status}")
```

### JavaScript

```javascript
import { Client } from '@qa-framework/sdk';

const client = new Client({ apiKey: 'your-api-key' });

// Create suite
const suite = await client.suites.create({
  name: 'My Suite',
  description: 'Test suite'
});

// Run suite
const execution = await client.suites.run(suite.id);

// Check status
const status = await client.executions.get(execution.id);
console.log(`Status: ${status.status}`);
```

---

**Interactive API Docs:** https://qa-framework-backend.railway.app/docs
