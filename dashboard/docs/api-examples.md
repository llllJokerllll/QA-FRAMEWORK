# QA-Framework Dashboard API Examples

Complete request/response examples for all API endpoints with multi-language code samples.

## Table of Contents

- [Authentication](#authentication)
- [Test Suites](#test-suites)
- [Test Cases](#test-cases)
- [Executions](#executions)
- [Users](#users)
- [Dashboard](#dashboard)
- [Error Handling](#error-handling)
- [Pagination Examples](#pagination-examples)
- [Filtering Examples](#filtering-examples)

---

## Authentication

### Login

Obtain an access token for API authentication.

**Endpoint:** `POST /api/v1/auth/login`

**Request:**

```json
{
  "username": "admin",
  "password": "secure_password123"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsImV4cCI6MTcwNTM1MTIwMH0.sample",
  "token_type": "bearer"
}
```

#### Code Examples

**cURL:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "secure_password123"
  }'
```

**Python:**

```python
import requests

url = "http://localhost:8000/api/v1/auth/login"
payload = {
    "username": "admin",
    "password": "secure_password123"
}

response = requests.post(url, json=payload)
token = response.json()["access_token"]
print(f"Token: {token}")
```

**JavaScript (Node.js/fetch):**

```javascript
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'secure_password123'
  })
});

const data = await response.json();
const token = data.access_token;
console.log('Token:', token);
```

**JavaScript (Axios):**

```javascript
import axios from 'axios';

const response = await axios.post('http://localhost:8000/api/v1/auth/login', {
  username: 'admin',
  password: 'secure_password123'
});

const token = response.data.access_token;
```

---

## Test Suites

### Create Test Suite

Create a new test suite.

**Endpoint:** `POST /api/v1/suites`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**

```json
{
  "name": "API Integration Tests",
  "description": "Comprehensive API testing suite",
  "framework_type": "pytest",
  "config": {
    "parallel_workers": 4,
    "timeout": 300,
    "retry_count": 2
  }
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "name": "API Integration Tests",
  "description": "Comprehensive API testing suite",
  "framework_type": "pytest",
  "config": {
    "parallel_workers": 4,
    "timeout": 300,
    "retry_count": 2
  },
  "is_active": true,
  "created_by": 1,
  "created_at": "2024-01-15T10:30:45.123456Z",
  "updated_at": "2024-01-15T10:30:45.123456Z"
}
```

#### Code Examples

**cURL:**

```bash
curl -X POST "http://localhost:8000/api/v1/suites" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Integration Tests",
    "description": "Comprehensive API testing suite",
    "framework_type": "pytest",
    "config": {
      "parallel_workers": 4,
      "timeout": 300
    }
  }'
```

**Python:**

```python
import requests

url = "http://localhost:8000/api/v1/suites"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
payload = {
    "name": "API Integration Tests",
    "description": "Comprehensive API testing suite",
    "framework_type": "pytest",
    "config": {
        "parallel_workers": 4,
        "timeout": 300
    }
}

response = requests.post(url, headers=headers, json=payload)
suite = response.json()
print(f"Created suite ID: {suite['id']}")
```

**JavaScript:**

```javascript
const response = await fetch('http://localhost:8000/api/v1/suites', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'API Integration Tests',
    description: 'Comprehensive API testing suite',
    framework_type: 'pytest',
    config: {
      parallel_workers: 4,
      timeout: 300
    }
  })
});

const suite = await response.json();
```

---

### List Test Suites

Retrieve all test suites with pagination.

**Endpoint:** `GET /api/v1/suites`

**Query Parameters:**
- `skip` (int, optional): Number of items to skip (default: 0)
- `limit` (int, optional): Maximum items to return (default: 100)

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "name": "API Integration Tests",
    "description": "Comprehensive API testing suite",
    "framework_type": "pytest",
    "config": {
      "parallel_workers": 4,
      "timeout": 300
    },
    "is_active": true,
    "created_by": 1,
    "created_at": "2024-01-15T10:30:45.123456Z",
    "updated_at": "2024-01-15T10:30:45.123456Z"
  },
  {
    "id": 2,
    "name": "UI Automation Tests",
    "description": "Selenium-based UI tests",
    "framework_type": "pytest",
    "config": {
      "browser": "chrome",
      "headless": true
    },
    "is_active": true,
    "created_by": 1,
    "created_at": "2024-01-15T11:00:00.000000Z",
    "updated_at": "2024-01-15T11:00:00.000000Z"
  }
]
```

#### Code Examples

**cURL:**

```bash
# List all suites
curl "http://localhost:8000/api/v1/suites" \
  -H "Authorization: Bearer YOUR_TOKEN"

# With pagination
curl "http://localhost:8000/api/v1/suites?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Python:**

```python
import requests

url = "http://localhost:8000/api/v1/suites"
headers = {"Authorization": f"Bearer {token}"}
params = {"skip": 0, "limit": 10}

response = requests.get(url, headers=headers, params=params)
suites = response.json()

for suite in suites:
    print(f"ID: {suite['id']}, Name: {suite['name']}")
```

---

### Get Test Suite by ID

Retrieve a specific test suite.

**Endpoint:** `GET /api/v1/suites/{suite_id}`

**Response (200 OK):**

```json
{
  "id": 1,
  "name": "API Integration Tests",
  "description": "Comprehensive API testing suite",
  "framework_type": "pytest",
  "config": {
    "parallel_workers": 4,
    "timeout": 300
  },
  "is_active": true,
  "created_by": 1,
  "created_at": "2024-01-15T10:30:45.123456Z",
  "updated_at": "2024-01-15T10:30:45.123456Z"
}
```

**Response (404 Not Found):**

```json
{
  "detail": "Test suite not found"
}
```

#### Code Examples

**Python with Error Handling:**

```python
import requests

suite_id = 1
url = f"http://localhost:8000/api/v1/suites/{suite_id}"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    suite = response.json()
    print(f"Suite: {suite['name']}")
elif response.status_code == 404:
    print(f"Suite {suite_id} not found")
else:
    print(f"Error: {response.status_code}")
```

---

### Update Test Suite

Update an existing test suite.

**Endpoint:** `PUT /api/v1/suites/{suite_id}`

**Request:**

```json
{
  "name": "Updated API Integration Tests",
  "description": "Updated description",
  "config": {
    "parallel_workers": 8,
    "timeout": 600
  }
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "name": "Updated API Integration Tests",
  "description": "Updated description",
  "framework_type": "pytest",
  "config": {
    "parallel_workers": 8,
    "timeout": 600
  },
  "is_active": true,
  "created_by": 1,
  "created_at": "2024-01-15T10:30:45.123456Z",
  "updated_at": "2024-01-15T12:00:00.000000Z"
}
```

---

### Delete Test Suite

Soft delete a test suite.

**Endpoint:** `DELETE /api/v1/suites/{suite_id}`

**Response:** `204 No Content`

#### Code Examples

**cURL:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/suites/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Python:**

```python
import requests

suite_id = 1
url = f"http://localhost:8000/api/v1/suites/{suite_id}"
headers = {"Authorization": f"Bearer {token}"}

response = requests.delete(url, headers=headers)

if response.status_code == 204:
    print(f"Suite {suite_id} deleted successfully")
else:
    print(f"Error: {response.status_code}")
```

---

## Test Cases

### Create Test Case

Create a new test case within a suite.

**Endpoint:** `POST /api/v1/cases`

**Request:**

```json
{
  "suite_id": 1,
  "name": "Test User Login",
  "description": "Verify user can login with valid credentials",
  "test_code": "def test_user_login():\n    response = client.post('/login', json={'username': 'test', 'password': 'pass'})\n    assert response.status_code == 200",
  "test_type": "api",
  "priority": "high",
  "tags": ["smoke", "authentication"]
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "suite_id": 1,
  "name": "Test User Login",
  "description": "Verify user can login with valid credentials",
  "test_code": "def test_user_login():\n    response = client.post('/login', json={'username': 'test', 'password': 'pass'})\n    assert response.status_code == 200",
  "test_type": "api",
  "priority": "high",
  "tags": ["smoke", "authentication"],
  "is_active": true,
  "created_at": "2024-01-15T10:35:00.123456Z",
  "updated_at": "2024-01-15T10:35:00.123456Z"
}
```

#### Code Examples

**Python:**

```python
import requests

url = "http://localhost:8000/api/v1/cases"
headers = {"Authorization": f"Bearer {token}"}
payload = {
    "suite_id": 1,
    "name": "Test User Login",
    "description": "Verify user can login with valid credentials",
    "test_code": """def test_user_login():
    response = client.post('/login', json={'username': 'test', 'password': 'pass'})
    assert response.status_code == 200""",
    "test_type": "api",
    "priority": "high",
    "tags": ["smoke", "authentication"]
}

response = requests.post(url, headers=headers, json=payload)
case = response.json()
print(f"Created case ID: {case['id']}")
```

---

### List Test Cases

Retrieve test cases with optional suite filtering.

**Endpoint:** `GET /api/v1/cases`

**Query Parameters:**
- `suite_id` (int, optional): Filter by suite ID
- `skip` (int, optional): Pagination offset
- `limit` (int, optional): Maximum items

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "suite_id": 1,
    "name": "Test User Login",
    "description": "Verify user can login with valid credentials",
    "test_code": "def test_user_login():...",
    "test_type": "api",
    "priority": "high",
    "tags": ["smoke", "authentication"],
    "is_active": true,
    "created_at": "2024-01-15T10:35:00.123456Z",
    "updated_at": "2024-01-15T10:35:00.123456Z"
  }
]
```

**Filter by Suite:**

```bash
curl "http://localhost:8000/api/v1/cases?suite_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Get Test Case by ID

**Endpoint:** `GET /api/v1/cases/{case_id}`

**Response (200 OK):**

```json
{
  "id": 1,
  "suite_id": 1,
  "name": "Test User Login",
  "description": "Verify user can login with valid credentials",
  "test_code": "def test_user_login():...",
  "test_type": "api",
  "priority": "high",
  "tags": ["smoke", "authentication"],
  "is_active": true,
  "created_at": "2024-01-15T10:35:00.123456Z",
  "updated_at": "2024-01-15T10:35:00.123456Z"
}
```

---

### Update Test Case

**Endpoint:** `PUT /api/v1/cases/{case_id}`

**Request:**

```json
{
  "name": "Updated Test User Login",
  "priority": "critical",
  "tags": ["smoke", "authentication", "regression"]
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "suite_id": 1,
  "name": "Updated Test User Login",
  "description": "Verify user can login with valid credentials",
  "test_code": "def test_user_login():...",
  "test_type": "api",
  "priority": "critical",
  "tags": ["smoke", "authentication", "regression"],
  "is_active": true,
  "created_at": "2024-01-15T10:35:00.123456Z",
  "updated_at": "2024-01-15T12:00:00.000000Z"
}
```

---

### Delete Test Case

**Endpoint:** `DELETE /api/v1/cases/{case_id}`

**Response:** `204 No Content`

---

## Executions

### Create Execution

Create a new test execution.

**Endpoint:** `POST /api/v1/executions`

**Request:**

```json
{
  "suite_id": 1,
  "execution_type": "manual",
  "environment": "staging"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "suite_id": 1,
  "execution_type": "manual",
  "environment": "staging",
  "executed_by": 1,
  "started_at": "2024-01-15T10:40:00.123456Z",
  "ended_at": null,
  "duration": null,
  "status": "running",
  "total_tests": 0,
  "passed_tests": 0,
  "failed_tests": 0,
  "skipped_tests": 0,
  "results_summary": null,
  "artifacts_path": null
}
```

---

### List Executions

Retrieve executions with filtering options.

**Endpoint:** `GET /api/v1/executions`

**Query Parameters:**
- `suite_id` (int, optional): Filter by suite
- `status_filter` (string, optional): Filter by status (running, passed, failed, skipped, error)
- `skip` (int, optional): Pagination offset
- `limit` (int, optional): Maximum items

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "suite_id": 1,
    "execution_type": "manual",
    "environment": "staging",
    "executed_by": 1,
    "started_at": "2024-01-15T10:40:00.123456Z",
    "ended_at": "2024-01-15T10:45:30.123456Z",
    "duration": 330,
    "status": "passed",
    "total_tests": 50,
    "passed_tests": 48,
    "failed_tests": 2,
    "skipped_tests": 0,
    "results_summary": {
      "success_rate": 96.0,
      "avg_duration": 6.6
    },
    "artifacts_path": "/executions/1"
  }
]
```

**Filter by Status:**

```bash
# Get failed executions
curl "http://localhost:8000/api/v1/executions?status_filter=failed" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get executions for specific suite
curl "http://localhost:8000/api/v1/executions?suite_id=1&limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Get Execution by ID

**Endpoint:** `GET /api/v1/executions/{execution_id}`

**Response (200 OK):**

```json
{
  "id": 1,
  "suite_id": 1,
  "execution_type": "manual",
  "environment": "staging",
  "executed_by": 1,
  "started_at": "2024-01-15T10:40:00.123456Z",
  "ended_at": "2024-01-15T10:45:30.123456Z",
  "duration": 330,
  "status": "passed",
  "total_tests": 50,
  "passed_tests": 48,
  "failed_tests": 2,
  "skipped_tests": 0,
  "results_summary": {
    "success_rate": 96.0,
    "avg_duration": 6.6,
    "slowest_tests": ["test_large_data_export", "test_complex_query"]
  },
  "artifacts_path": "/executions/1"
}
```

---

### Start Execution

Start a pending test execution.

**Endpoint:** `POST /api/v1/executions/{execution_id}/start`

**Response (200 OK):**

```json
{
  "message": "Execution started successfully",
  "execution_id": 1,
  "status": "running",
  "started_at": "2024-01-15T10:40:00.123456Z"
}
```

#### Code Examples

**Python:**

```python
import requests

execution_id = 1
url = f"http://localhost:8000/api/v1/executions/{execution_id}/start"
headers = {"Authorization": f"Bearer {token}"}

response = requests.post(url, headers=headers)
result = response.json()
print(f"Execution {result['execution_id']} started: {result['message']}")
```

---

### Stop Execution

Stop a running test execution.

**Endpoint:** `POST /api/v1/executions/{execution_id}/stop`

**Response (200 OK):**

```json
{
  "message": "Execution stopped successfully",
  "execution_id": 1,
  "status": "failed",
  "duration": 180
}
```

---

## Users

### Create User

Create a new user account.

**Endpoint:** `POST /api/v1/users`

**Request:**

```json
{
  "username": "john_doe",
  "email": "john.doe@example.com",
  "password": "SecurePass123!",
  "is_active": true
}
```

**Response (201 Created):**

```json
{
  "id": 2,
  "username": "john_doe",
  "email": "john.doe@example.com",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-15T10:50:00.123456Z",
  "updated_at": "2024-01-15T10:50:00.123456Z"
}
```

---

### List Users

Retrieve all users (requires authentication).

**Endpoint:** `GET /api/v1/users`

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_active": true,
    "is_superuser": true,
    "created_at": "2024-01-15T09:00:00.123456Z",
    "updated_at": "2024-01-15T09:00:00.123456Z"
  },
  {
    "id": 2,
    "username": "john_doe",
    "email": "john.doe@example.com",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2024-01-15T10:50:00.123456Z",
    "updated_at": "2024-01-15T10:50:00.123456Z"
  }
]
```

---

### Get User by ID

**Endpoint:** `GET /api/v1/users/{user_id}`

**Response (200 OK):**

```json
{
  "id": 2,
  "username": "john_doe",
  "email": "john.doe@example.com",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-15T10:50:00.123456Z",
  "updated_at": "2024-01-15T10:50:00.123456Z"
}
```

---

### Update User

**Endpoint:** `PUT /api/v1/users/{user_id}`

**Request:**

```json
{
  "email": "john.doe.new@example.com",
  "is_active": false
}
```

**Response (200 OK):**

```json
{
  "id": 2,
  "username": "john_doe",
  "email": "john.doe.new@example.com",
  "is_active": false,
  "is_superuser": false,
  "created_at": "2024-01-15T10:50:00.123456Z",
  "updated_at": "2024-01-15T12:00:00.000000Z"
}
```

---

### Delete User

**Endpoint:** `DELETE /api/v1/users/{user_id}`

**Response:** `204 No Content`

---

## Dashboard

### Get Dashboard Statistics

Retrieve comprehensive dashboard statistics.

**Endpoint:** `GET /api/v1/dashboard/stats`

**Response (200 OK):**

```json
{
  "total_suites": 15,
  "total_cases": 450,
  "total_executions": 1250,
  "active_executions": 3,
  "success_rate": 94.5,
  "avg_duration": 245.5,
  "last_24h_executions": 45,
  "pending_executions": 2
}
```

#### Code Examples

**Python:**

```python
import requests

url = "http://localhost:8000/api/v1/dashboard/stats"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
stats = response.json()

print(f"Total Suites: {stats['total_suites']}")
print(f"Success Rate: {stats['success_rate']}%")
print(f"Active Executions: {stats['active_executions']}")
```

**JavaScript:**

```javascript
const response = await fetch('http://localhost:8000/api/v1/dashboard/stats', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const stats = await response.json();
console.log(`Success Rate: ${stats.success_rate}%`);
```

---

### Get Execution Trends

Retrieve execution trends over time.

**Endpoint:** `GET /api/v1/dashboard/trends`

**Query Parameters:**
- `days` (int, optional): Number of days to include (default: 30, max: 365)

**Response (200 OK):**

```json
[
  {
    "date": "2024-01-01",
    "executions": 15,
    "passed": 14,
    "failed": 1,
    "success_rate": 93.3
  },
  {
    "date": "2024-01-02",
    "executions": 20,
    "passed": 19,
    "failed": 1,
    "success_rate": 95.0
  },
  {
    "date": "2024-01-03",
    "executions": 10,
    "passed": 10,
    "failed": 0,
    "success_rate": 100.0
  }
]
```

**Get 7-day trends:**

```bash
curl "http://localhost:8000/api/v1/dashboard/trends?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Error Handling

### Common Error Responses

**400 Bad Request - Validation Error:**

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**401 Unauthorized:**

```json
{
  "detail": "Invalid authentication credentials"
}
```

**403 Forbidden:**

```json
{
  "detail": "Not enough permissions"
}
```

**404 Not Found:**

```json
{
  "detail": "Test suite not found"
}
```

**422 Unprocessable Entity:**

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

**429 Too Many Requests:**

```json
{
  "detail": "Rate limit exceeded"
}
```

### Error Handling Pattern

**Python with Comprehensive Error Handling:**

```python
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

def api_request_with_error_handling(method, url, **kwargs):
    """Make API request with comprehensive error handling."""
    try:
        response = requests.request(method, url, timeout=30, **kwargs)
        
        # Handle different status codes
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 201:
            return response.json()
        elif response.status_code == 204:
            return None
        elif response.status_code == 400:
            raise ValueError(f"Bad request: {response.json()}")
        elif response.status_code == 401:
            raise PermissionError("Authentication required or invalid token")
        elif response.status_code == 403:
            raise PermissionError("Insufficient permissions")
        elif response.status_code == 404:
            raise FileNotFoundError(f"Resource not found: {url}")
        elif response.status_code == 422:
            raise ValueError(f"Validation error: {response.json()}")
        elif response.status_code == 429:
            raise RuntimeError("Rate limit exceeded. Please retry later.")
        elif response.status_code >= 500:
            raise RuntimeError(f"Server error: {response.status_code}")
        else:
            response.raise_for_status()
            
    except Timeout:
        raise RuntimeError("Request timed out")
    except ConnectionError:
        raise RuntimeError("Failed to connect to API")
    except RequestException as e:
        raise RuntimeError(f"Request failed: {str(e)}")

# Usage
url = "http://localhost:8000/api/v1/suites/999"
headers = {"Authorization": f"Bearer {token}"}

try:
    result = api_request_with_error_handling("GET", url, headers=headers)
    print(f"Success: {result}")
except FileNotFoundError as e:
    print(f"Not found: {e}")
except PermissionError as e:
    print(f"Auth error: {e}")
except ValueError as e:
    print(f"Validation error: {e}")
except RuntimeError as e:
    print(f"Runtime error: {e}")
```

**JavaScript with Error Handling:**

```javascript
async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      
      switch (response.status) {
        case 400:
          throw new Error(`Bad request: ${error.detail}`);
        case 401:
          throw new Error('Authentication required');
        case 403:
          throw new Error('Insufficient permissions');
        case 404:
          throw new Error('Resource not found');
        case 422:
          throw new Error(`Validation error: ${JSON.stringify(error.detail)}`);
        case 429:
          throw new Error('Rate limit exceeded');
        case 500:
          throw new Error('Server error');
        default:
          throw new Error(`HTTP error: ${response.status}`);
      }
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// Usage
try {
  const suite = await apiRequest('http://localhost:8000/api/v1/suites/1', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  console.log('Suite:', suite);
} catch (error) {
  console.error('Error:', error.message);
}
```

---

## Pagination Examples

### Basic Pagination

**Python - Paginated Fetch:**

```python
import requests

def fetch_all_paginated(url, headers, batch_size=100):
    """Fetch all items using pagination."""
    all_items = []
    skip = 0
    
    while True:
        params = {'skip': skip, 'limit': batch_size}
        response = requests.get(url, headers=headers, params=params)
        items = response.json()
        
        if not items:
            break
        
        all_items.extend(items)
        
        # Check if we've got less than the limit (last page)
        if len(items) < batch_size:
            break
        
        skip += batch_size
    
    return all_items

# Fetch all suites
url = "http://localhost:8000/api/v1/suites"
headers = {"Authorization": f"Bearer {token}"}
all_suites = fetch_all_paginated(url, headers)
print(f"Total suites fetched: {len(all_suites)}")
```

**JavaScript - Paginated Fetch:**

```javascript
async function fetchAllPaginated(url, headers, batchSize = 100) {
  const allItems = [];
  let skip = 0;
  let hasMore = true;

  while (hasMore) {
    const response = await fetch(`${url}?skip=${skip}&limit=${batchSize}`, {
      headers
    });
    const items = await response.json();

    if (items.length === 0) {
      break;
    }

    allItems.push(...items);
    hasMore = items.length === batchSize;
    skip += batchSize;
  }

  return allItems;
}

// Usage
const suites = await fetchAllPaginated(
  'http://localhost:8000/api/v1/suites',
  { 'Authorization': `Bearer ${token}` }
);
console.log(`Total suites: ${suites.length}`);
```

### Pagination with Progress Tracking

**Python with Progress Bar:**

```python
import requests
from tqdm import tqdm

def fetch_with_progress(url, headers, batch_size=50):
    """Fetch all items with progress tracking."""
    all_items = []
    skip = 0
    
    # Get first page to estimate total
    params = {'skip': 0, 'limit': 1}
    response = requests.get(url, headers=headers, params=params)
    
    # If API returns total count, use it; otherwise estimate
    total_estimate = None
    
    with tqdm(desc="Fetching items", unit="items") as pbar:
        while True:
            params = {'skip': skip, 'limit': batch_size}
            response = requests.get(url, headers=headers, params=params)
            items = response.json()
            
            if not items:
                break
            
            all_items.extend(items)
            pbar.update(len(items))
            
            if len(items) < batch_size:
                break
            
            skip += batch_size
    
    return all_items

# Usage
url = "http://localhost:8000/api/v1/cases"
all_cases = fetch_with_progress(url, {"Authorization": f"Bearer {token}"})
```

---

## Filtering Examples

### Filter by Multiple Criteria

**Python - Complex Filtering:**

```python
import requests

def get_filtered_executions(token, **filters):
    """Get executions with multiple filters."""
    url = "http://localhost:8000/api/v1/executions"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Build query parameters
    params = {}
    if 'suite_id' in filters:
        params['suite_id'] = filters['suite_id']
    if 'status' in filters:
        params['status_filter'] = filters['status']
    if 'limit' in filters:
        params['limit'] = filters['limit']
    if 'skip' in filters:
        params['skip'] = filters['skip']
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Get failed executions for suite 1
failed = get_filtered_executions(
    token,
    suite_id=1,
    status='failed',
    limit=10
)

# Get recent passed executions
passed = get_filtered_executions(
    token,
    status='passed',
    limit=20
)

print(f"Failed: {len(failed)}, Passed: {len(passed)}")
```

**Filter Test Cases by Suite:**

```python
import requests

def get_cases_by_suite(token, suite_id):
    """Get all test cases for a specific suite."""
    url = "http://localhost:8000/api/v1/cases"
    headers = {"Authorization": f"Bearer {token}"}
    
    all_cases = []
    skip = 0
    limit = 100
    
    while True:
        params = {
            'suite_id': suite_id,
            'skip': skip,
            'limit': limit
        }
        response = requests.get(url, headers=headers, params=params)
        cases = response.json()
        
        if not cases:
            break
        
        all_cases.extend(cases)
        
        if len(cases) < limit:
            break
        
        skip += limit
    
    return all_cases

# Get all cases for suite 1
cases = get_cases_by_suite(token, suite_id=1)
print(f"Total cases in suite: {len(cases)}")

# Filter by priority
high_priority = [c for c in cases if c['priority'] == 'high']
print(f"High priority cases: {len(high_priority)}")

# Filter by tag
smoke_tests = [c for c in cases if 'smoke' in c.get('tags', [])]
print(f"Smoke tests: {len(smoke_tests)}")
```

**JavaScript - Filter Executions:**

```javascript
async function getFilteredExecutions(token, filters = {}) {
  const params = new URLSearchParams();
  
  if (filters.suiteId) params.append('suite_id', filters.suiteId);
  if (filters.status) params.append('status_filter', filters.status);
  if (filters.limit) params.append('limit', filters.limit);
  if (filters.skip) params.append('skip', filters.skip);
  
  const url = `http://localhost:8000/api/v1/executions?${params}`;
  const response = await fetch(url, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  return response.json();
}

// Usage
const recentFailed = await getFilteredExecutions(token, {
  status: 'failed',
  limit: 10
});

const suiteExecutions = await getFilteredExecutions(token, {
  suiteId: 1,
  limit: 50
});
```

**cURL - Filter Examples:**

```bash
# Get all failed executions
curl "http://localhost:8000/api/v1/executions?status_filter=failed" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get executions for suite 1 with status passed
curl "http://localhost:8000/api/v1/executions?suite_id=1&status_filter=passed" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get test cases for specific suite
curl "http://localhost:8000/api/v1/cases?suite_id=1&limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get trends for last 7 days
curl "http://localhost:8000/api/v1/dashboard/trends?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Complete Integration Example

**Python - Full CRUD Workflow:**

```python
import requests
import time

class QAFrameworkClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def login(self, username, password):
        """Authenticate and store token."""
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={'username': username, 'password': password}
        )
        response.raise_for_status()
        self.token = response.json()['access_token']
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}'
        })
        return self.token
    
    def create_suite(self, name, description=None, framework='pytest'):
        """Create a test suite."""
        payload = {
            'name': name,
            'description': description,
            'framework_type': framework,
            'config': {}
        }
        response = self.session.post(
            f"{self.base_url}/suites",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def create_case(self, suite_id, name, test_code, test_type='api'):
        """Create a test case."""
        payload = {
            'suite_id': suite_id,
            'name': name,
            'test_code': test_code,
            'test_type': test_type,
            'priority': 'medium',
            'tags': []
        }
        response = self.session.post(
            f"{self.base_url}/cases",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def execute_suite(self, suite_id, environment='production'):
        """Create and start execution."""
        # Create execution
        exec_payload = {
            'suite_id': suite_id,
            'execution_type': 'manual',
            'environment': environment
        }
        exec_response = self.session.post(
            f"{self.base_url}/executions",
            json=exec_payload
        )
        exec_response.raise_for_status()
        execution = exec_response.json()
        
        # Start execution
        self.session.post(
            f"{self.base_url}/executions/{execution['id']}/start"
        )
        
        return execution
    
    def wait_for_execution(self, execution_id, timeout=300):
        """Wait for execution to complete."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = self.session.get(
                f"{self.base_url}/executions/{execution_id}"
            )
            response.raise_for_status()
            execution = response.json()
            
            if execution['status'] != 'running':
                return execution
            
            time.sleep(5)
        
        raise TimeoutError(f"Execution {execution_id} did not complete within {timeout}s")
    
    def get_dashboard_stats(self):
        """Get dashboard statistics."""
        response = self.session.get(f"{self.base_url}/dashboard/stats")
        response.raise_for_status()
        return response.json()


# Complete workflow example
if __name__ == "__main__":
    # Initialize client
    client = QAFrameworkClient("http://localhost:8000/api/v1")
    
    # Login
    client.login("admin", "secure_password123")
    print("✓ Logged in successfully")
    
    # Create suite
    suite = client.create_suite(
        name="API Smoke Tests",
        description="Critical API endpoint tests",
        framework="pytest"
    )
    print(f"✓ Created suite: {suite['name']} (ID: {suite['id']})")
    
    # Create test case
    case = client.create_case(
        suite_id=suite['id'],
        name="Health Check Test",
        test_code="""
def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'
""",
        test_type="api"
    )
    print(f"✓ Created test case: {case['name']} (ID: {case['id']})")
    
    # Execute suite
    execution = client.execute_suite(suite['id'], environment='staging')
    print(f"✓ Started execution ID: {execution['id']}")
    
    # Wait for completion
    print("Waiting for execution to complete...")
    result = client.wait_for_execution(execution['id'])
    print(f"✓ Execution completed with status: {result['status']}")
    print(f"  - Total tests: {result['total_tests']}")
    print(f"  - Passed: {result['passed_tests']}")
    print(f"  - Failed: {result['failed_tests']}")
    
    # Get dashboard stats
    stats = client.get_dashboard_stats()
    print(f"\nDashboard Stats:")
    print(f"  - Total suites: {stats['total_suites']}")
    print(f"  - Success rate: {stats['success_rate']}%")
```

---

## Additional Resources

- [API Guide](api-guide.md) - Authentication, patterns, and best practices
- [Architecture](architecture.md) - System architecture and components
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
