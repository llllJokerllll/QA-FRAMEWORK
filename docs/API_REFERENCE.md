# API Reference - QA-FRAMEWORK SaaS

**Version:** 1.0.0
**Base URL:** `https://qa-framework-production.up.railway.app/api/v1`
**Documentation:** https://qa-framework-production.up.railway.app/api/v1/docs

---

## Authentication

### POST /api/v1/auth/login
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "plan": "free"
  }
}
```

### POST /api/v1/auth/register
Register a new user.

**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "secure_password",
  "name": "John Doe"
}
```

**Response (201):**
```json
{
  "user": {
    "id": "uuid",
    "email": "newuser@example.com",
    "name": "John Doe",
    "plan": "free",
    "created_at": "2026-03-03T00:00:00Z"
  },
  "message": "Registration successful. Please check your email for verification."
}
```

### POST /api/v1/auth/refresh
Refresh access token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### POST /api/v1/auth/logout
Logout and revoke current tokens.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):**
No content.

### GET /api/v1/auth/api-keys
Get user's API keys.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "api_keys": [
    {
      "id": "uuid",
      "name": "Production Key",
      "key": "sk_live_***",
      "created_at": "2026-03-03T00:00:00Z",
      "last_used": "2026-03-03T10:00:00Z"
    }
  ]
}
```

---

## Billing

### GET /api/v1/billing/plans
Get available subscription plans.

**Response (200):**
```json
{
  "plans": [
    {
      "name": "free",
      "price": 0,
      "currency": "usd",
      "interval": "month",
      "features": [
        "1,000 API calls/month",
        "1 test suite",
        "Basic support"
      ],
      "limits": {
        "api_calls": 1000,
        "test_suites": 1,
        "storage_mb": 100
      }
    },
    {
      "name": "pro",
      "price": 99,
      "currency": "usd",
      "interval": "month",
      "features": [
        "10,000 API calls/month",
        "10 test suites",
        "Priority support",
        "AI test generation",
        "Self-healing tests"
      ],
      "limits": {
        "api_calls": 10000,
        "test_suites": 10,
        "storage_mb": 1000,
        "bandwidth_mb": 1000
      }
    },
    {
      "name": "enterprise",
      "price": 499,
      "currency": "usd",
      "interval": "month",
      "features": [
        "Unlimited API calls",
        "Unlimited test suites",
        "24/7 dedicated support",
        "Advanced AI features",
        "Custom integrations"
      ],
      "limits": {
        "api_calls": -1,
        "test_suites": -1,
        "storage_mb": 10000,
        "bandwidth_mb": 10000
      }
    }
  ]
}
```

### GET /api/v1/billing/subscription
Get current user's subscription.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "plan": {
    "name": "pro",
    "price": 99,
    "currency": "usd"
  },
  "status": "active",
  "current_period_start": "2026-02-01T00:00:00Z",
  "current_period_end": "2026-03-01T00:00:00Z",
  "cancel_at_period_end": false,
  "cancel_at": null
}
```

### POST /api/v1/billing/subscribe
Subscribe to a plan.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "plan": "pro",
  "payment_method": "pm_card_visa"
}
```

**Response (200):**
```json
{
  "success": true,
  "subscription": {
    "id": "sub_123456789",
    "status": "active",
    "plan": "pro",
    "current_period_start": "2026-03-03T00:00:00Z",
    "current_period_end": "2026-04-03T00:00:00Z"
  }
}
```

### POST /api/v1/billing/subscription/cancel
Cancel current subscription.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "subscription": {
    "id": "sub_123456789",
    "status": "past_due",
    "cancel_at_period_end": true
  }
}
```

### POST /api/v1/billing/subscription/resume
Resume cancelled subscription.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "subscription": {
    "id": "sub_123456789",
    "status": "active",
    "cancel_at_period_end": false
  }
}
```

### POST /api/v1/billing/webhook
Stripe webhook endpoint (webhook_secret required).

**Headers:**
```
stripe-signature: <signature>
```

**Body:**
Webhook payload from Stripe.

---

## Test Management

### POST /api/v1/tests/run
Run a test suite.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "suite_id": "uuid",
  "framework": "pytest",
  "options": {
    "parallel": true,
    "timeout": 300
  }
}
```

**Response (202):**
```json
{
  "job_id": "job_123456789",
  "status": "queued",
  "message": "Test suite started"
}
```

### GET /api/v1/tests/jobs/{job_id}
Get test job status.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "job_id": "job_123456789",
  "status": "completed",
  "started_at": "2026-03-03T10:00:00Z",
  "completed_at": "2026-03-03T10:05:00Z",
  "total_tests": 100,
  "passed": 95,
  "failed": 3,
  "skipped": 2,
  "duration_ms": 300000,
  "test_suites": [
    {
      "name": "core_tests",
      "passed": 50,
      "failed": 1,
      "duration_ms": 150000
    }
  ]
}
```

### GET /api/v1/tests/results/{result_id}
Get detailed test results.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "result_id": "result_123456789",
  "job_id": "job_123456789",
  "suite_id": "uuid",
  "framework": "pytest",
  "total_tests": 100,
  "passed": 95,
  "failed": 3,
  "skipped": 2,
  "duration_ms": 300000,
  "tests": [
    {
      "name": "test_user_login_success",
      "status": "passed",
      "duration_ms": 150,
      "error_message": null,
      "traceback": null,
      "tags": ["smoke", "auth"]
    },
    {
      "name": "test_user_login_invalid_password",
      "status": "failed",
      "duration_ms": 200,
      "error_message": "AssertionError: Expected status 401, got 200",
      "traceback": "File \"test_auth.py\", line 45, in test_user_login_invalid_password\nassert response.status_code == 401",
      "tags": ["auth", "negative"]
    }
  ]
}
```

### POST /api/v1/tests/generate
Generate tests from requirements (AI-powered).

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "requirements": "User should be able to reset password via email",
  "framework": "pytest",
  "language": "python",
  "context": {
    "module_path": "auth.password_reset"
  }
}
```

**Response (200):**
```json
{
  "tests_generated": [
    {
      "name": "test_password_reset_email_sent",
      "code": "def test_password_reset_email_sent():\n    # Implementation\n    pass",
      "status": "generated",
      "confidence": 0.95
    }
  ],
  "total_tests": 1,
  "avg_confidence": 0.95,
  "generation_time_ms": 1250
}
```

---

## Self-Healing

### GET /api/v1/self-healing/selectors
Get selector healing recommendations.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "selectors": [
    {
      "selector_type": "css",
      "value": ".user-menu-button",
      "test_id": "test_123",
      "test_name": "test_user_menu",
      "failure_count": 5,
      "confidence_score": 0.35,
      "recommendations": [
        {
          "type": "attribute",
          "new_value": "button[data-testid='user-menu']",
          "confidence": 0.75
        },
        {
          "type": "id",
          "new_value": "user-menu-btn",
          "confidence": 0.80
        }
      ]
    }
  ],
  "total_recommendations": 2,
  "low_confidence_count": 3
}
```

### POST /api/v1/self-healing/heal
Apply healing recommendation.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "test_id": "test_123",
  "selector_type": "css",
  "old_value": ".user-menu-button",
  "new_value": "button[data-testid='user-menu']"
}
```

**Response (200):**
```json
{
  "success": true,
  "healing_session_id": "heal_123456789",
  "status": "healed",
  "changes": [
    {
      "file": "tests/test_auth.py",
      "line_number": 45,
      "old": '.user-menu-button',
      "new": 'button[data-testid="user-menu"]'
    }
  ]
}
```

### GET /api/v1/self-healing/sessions/{session_id}
Get healing session details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "session_id": "heal_123456789",
  "status": "completed",
  "total_selectors_healed": 5,
  "total_tests_rewritten": 3,
  "confidence_improved": 0.82,
  "started_at": "2026-03-03T10:00:00Z",
  "completed_at": "2026-03-03T10:05:00Z",
  "results": {
    "low_confidence": 3,
    "healed": 2,
    "kept": 1
  }
}
```

---

## Flaky Test Detection

### GET /api/v1/flaky-detection/quarantine
Get quarantined tests.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "quarantined_tests": [
    {
      "test_id": "test_123",
      "test_name": "test_payment_processing",
      "detected_flaky": true,
      "failure_rate": 0.75,
      "last_failure": "2026-03-02T10:00:00Z",
      "quarantine_reason": "timing_based",
      "detected_by": "sequence_analysis",
      "status": "quarantined",
      "recommendations": [
        "Add retry logic with exponential backoff",
        "Implement proper cleanup between tests",
        "Use deterministic fixtures"
      ]
    }
  ],
  "total_quarantined": 5,
  "total_flaky_tests": 8
}
```

### POST /api/v1/flaky-detection/quarantine/{test_id}/evaluate
Evaluate test for quarantine release.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "reason": "timing_fixed",
  "comments": "Fixed race condition by adding sleep(0.1)"
}
```

**Response (200):**
```json
{
  "success": true,
  "can_be_released": true,
  "recommendations": [
    "Monitor for 3 more runs before release",
    "Add stability metrics"
  ]
}
```

### GET /api/v1/flaky-detection/diagnostics/{test_id}
Get root cause analysis for flaky test.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "test_id": "test_123",
  "test_name": "test_payment_processing",
  "analysis": {
    "primary_issue": "timing_race_condition",
    "secondary_issues": [
      "inconsistent_fixture_state",
      "external_api_dependency"
    ],
    "failure_patterns": [
      {
        "pattern": "failing on first run, passing on second",
        "occurrences": 15,
        "confidence": 0.95
      }
    ],
    "recommendations": [
      "Add explicit synchronization",
      "Use event-driven architecture",
      "Mock external dependencies",
      "Add flakiness guard rails"
    ],
    "risk_level": "high"
  }
}
```

---

## Feedback

### POST /api/v1/feedback
Submit feedback.

**Headers:**
```
Content-Type: application/json
```

**Request:**
```json
{
  "type": "bug",
  "category": "dashboard",
  "rating": 3,
  "message": "The download button doesn't work on Firefox",
  "tags": ["firefox", "download"],
  "anonymous": false
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Thank you for your feedback!",
  "feedback_id": "fb_123456789"
}
```

### GET /api/v1/feedback
Get feedback (admin only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: filter by status (new, in_progress, resolved, closed)
- `type`: filter by type (bug, feature, general, improvement)
- `page`: page number
- `limit`: items per page

**Response (200):**
```json
{
  "feedback": [
    {
      "id": "fb_123456789",
      "type": "bug",
      "category": "dashboard",
      "rating": 3,
      "message": "The download button doesn't work on Firefox",
      "tags": ["firefox", "download"],
      "status": "new",
      "created_at": "2026-03-03T10:00:00Z",
      "updated_at": "2026-03-03T10:00:00Z",
      "user": {
        "id": "uuid",
        "name": "John Doe"
      }
    }
  ],
  "total": 25,
  "page": 1,
  "limit": 10
}
```

### GET /api/v1/feedback/stats
Get feedback statistics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "total_feedback": 150,
  "by_status": {
    "new": 45,
    "in_progress": 30,
    "resolved": 60,
    "closed": 15
  },
  "by_type": {
    "bug": 80,
    "feature": 40,
    "general": 20,
    "improvement": 10
  },
  "average_rating": 4.2,
  "rating_distribution": {
    "1": 5,
    "2": 10,
    "3": 25,
    "4": 50,
    "5": 60
  }
}
```

---

## Beta Signup

### POST /api/v1/beta/signup
Sign up for beta program.

**Headers:**
```
Content-Type: application/json
```

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "team_size": 10,
  "use_case": "ecommerce_testing",
  "utm_source": "referral",
  "utm_campaign": "beta_launch"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Welcome to the beta! Check your email for next steps.",
  "signup_id": "beta_123456789",
  "status": "pending",
  "estimated_review": "2-3 business days"
}
```

### GET /api/v1/beta/check/{email}
Check if email is already signed up.

**Headers:**
```
Content-Type: application/json
```

**Response (200):**
```json
{
  "email": "john@example.com",
  "status": "registered",
  "signup_id": "beta_123456789"
}
```

**Response (404):**
```json
{
  "email": "john@example.com",
  "status": "not_registered"
}
```

### GET /api/v1/beta/stats
Get beta program statistics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "total_signups": 500,
  "approved": 450,
  "pending": 30,
  "rejected": 20,
  "conversion_rate": 0.90,
  "avg_team_size": 8,
  "top_use_cases": [
    "ecommerce_testing": 150,
    "api_testing": 100,
    "mobile_testing": 75
  ]
}
```

---

## Analytics

### GET /api/v1/analytics/dashboard
Get analytics dashboard data.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "kpi": {
    "total_tests": 12500,
    "success_rate": 98.5,
    "active_users": 350,
    "mrr": 12450,
    "revenue_growth": 12.5
  },
  "tests_trend": {
    "labels": ["Jan", "Feb", "Mar"],
    "data": [8500, 10500, 12500]
  },
  "feature_usage": {
    "self_healing": 45,
    "ai_generation": 32,
    "flaky_detection": 28,
    "usage_percentages": [45, 32, 23]
  },
  "recent_signups": [
    {
      "id": "uuid",
      "name": "John Doe",
      "signup_date": "2026-03-01T10:00:00Z"
    }
  ]
}
```

### GET /api/v1/analytics/users
Get user analytics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "total_users": 350,
  "new_users_last_month": 45,
  "active_users": 250,
  "churn_rate": 0.05,
  "user_retention": 0.85,
  "plan_distribution": {
    "free": 150,
    "pro": 120,
    "enterprise": 80
  }
}
```

### GET /api/v1/analytics/tests
Get test analytics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "total_tests_run": 12500,
  "tests_this_month": 3500,
  "success_rate": 98.5,
  "flaky_tests_detected": 45,
  "self_healing_attempts": 120,
  "self_healing_success_rate": 0.85,
  "tests_by_framework": {
    "pytest": 7500,
    "cypress": 3000,
    "playwright": 2000
  }
}
```

### GET /api/v1/analytics/revenue
Get revenue analytics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "mrr": 12450,
  "arr": 149400,
  "monthly_revenue": {
    "current": 12450,
    "previous": 11000,
    "growth": 13.18
  },
  "revenue_by_plan": {
    "pro": 9900,
    "enterprise": 2550
  },
  "churned_mrr": 600,
  "churn_rate": 0.048
}
```

### GET /api/v1/analytics/features
Get feature usage analytics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "self_healing": {
    "enabled_users": 150,
    "usage_rate": 0.43,
    "avg_healings_per_user": 2.5,
    "success_rate": 0.85
  },
  "ai_generation": {
    "enabled_users": 120,
    "usage_rate": 0.34,
    "avg_generations_per_user": 5.2
  },
  "flaky_detection": {
    "enabled_users": 100,
    "usage_rate": 0.29,
    "avg_quarantines_per_user": 0.8
  }
}
```

---

## Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created
- **204 No Content**: Request successful, no content to return
- **400 Bad Request**: Invalid request
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Conflict with existing resource
- **422 Unprocessable Entity**: Validation failed
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: Service temporarily unavailable

---

## Rate Limiting

| Endpoint Type | Rate Limit |
|---------------|------------|
| Auth endpoints | 100 requests/minute |
| Public endpoints | 1000 requests/minute |
| User endpoints | 1000 requests/minute |
| Admin endpoints | 500 requests/minute |

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 2026-03-03T11:00:00Z
```

---

## Webhooks

### Available Webhook Events

- `subscription.created`
- `subscription.updated`
- `subscription.cancelled`
- `subscription.payment_failed`
- `test.run.completed`
- `self_healing.applied`
- `flaky_test.detected`

### Webhook Payload Example

```json
{
  "event": "subscription.updated",
  "data": {
    "subscription_id": "sub_123456789",
    "plan": "pro",
    "status": "active",
    "previous_plan": "free",
    "changes": ["plan"]
  },
  "timestamp": "2026-03-03T10:00:00Z",
  "signature": "sha256=abc123..."
}
```

---

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": {
      "field": "password",
      "suggestion": "Ensure your password is at least 8 characters"
    }
  }
}
```

Common error codes:
- `INVALID_CREDENTIALS`: Invalid login credentials
- `USER_EXISTS`: Email already registered
- `INVALID_PLAN`: Invalid subscription plan
- `QUOTA_EXCEEDED`: Usage limit exceeded
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `VALIDATION_ERROR`: Request validation failed

---

**Last Updated:** 2026-03-03
**Maintained by:** QA-FRAMEWORK Team
