"""
Granular Rate Limiting for QA-Framework API
Different limits for different endpoint types
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
from typing import Dict, Optional


class RateLimitConfig:
    """Rate limit configurations for different endpoint types."""
    
    # Read operations (GET)
    READ_REQUESTS = 200  # per minute
    READ_WINDOW = 60  # seconds
    
    # Write operations (POST, PUT, PATCH)
    WRITE_REQUESTS = 50  # per minute
    WRITE_WINDOW = 60  # seconds
    
    # Execution operations (test runs)
    EXECUTION_REQUESTS = 10  # per minute
    EXECUTION_WINDOW = 60  # seconds
    
    # Auth endpoints (login, register)
    AUTH_REQUESTS = 5  # per minute
    AUTH_WINDOW = 60  # seconds


class GranularRateLimiter:
    """Granular rate limiter with per-endpoint limits."""
    
    def __init__(self):
        # Store request counts: {client_ip: {endpoint_type: [(timestamp, count)]}}
        self.request_history: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        
        # Endpoint type mapping
        self.endpoint_types = {
            # Auth endpoints
            "POST /api/v1/auth/login": "auth",
            "POST /api/v1/auth/register": "auth",
            "POST /api/v1/auth/refresh": "auth",
            
            # Execution endpoints
            "POST /api/v1/executions": "execution",
            "POST /api/v1/executions/run": "execution",
            "POST /api/v1/suites/{suite_id}/run": "execution",
            
            # Write endpoints (default for POST, PUT, PATCH)
            "write": "write",
            
            # Read endpoints (default for GET)
            "read": "read",
        }
    
    def get_endpoint_type(self, method: str, path: str) -> str:
        """Determine endpoint type from method and path."""
        # Check exact matches first
        exact_key = f"{method} {path}"
        if exact_key in self.endpoint_types:
            return self.endpoint_types[exact_key]
        
        # Check pattern matches
        for pattern, endpoint_type in self.endpoint_types.items():
            if pattern.startswith(method) and pattern.split()[0] == method:
                return endpoint_type
        
        # Default based on method
        if method == "GET":
            return "read"
        elif method in ["POST", "PUT", "PATCH"]:
            # Check if it's an execution endpoint
            if "execution" in path or "run" in path:
                return "execution"
            return "write"
        
        return "read"
    
    def get_limit_config(self, endpoint_type: str) -> tuple:
        """Get rate limit configuration for endpoint type."""
        configs = {
            "auth": (RateLimitConfig.AUTH_REQUESTS, RateLimitConfig.AUTH_WINDOW),
            "execution": (RateLimitConfig.EXECUTION_REQUESTS, RateLimitConfig.EXECUTION_WINDOW),
            "write": (RateLimitConfig.WRITE_REQUESTS, RateLimitConfig.WRITE_WINDOW),
            "read": (RateLimitConfig.READ_REQUESTS, RateLimitConfig.READ_WINDOW),
        }
        return configs.get(endpoint_type, configs["read"])
    
    def is_allowed(self, client_ip: str, endpoint_type: str) -> tuple[bool, dict]:
        """
        Check if request is allowed.
        
        Returns:
            tuple: (allowed: bool, info: dict with remaining/limit/reset)
        """
        current_time = time.time()
        max_requests, window = self.get_limit_config(endpoint_type)
        
        # Clean old entries
        history = self.request_history[client_ip][endpoint_type]
        history[:] = [(t, c) for t, c in history if current_time - t < window]
        
        # Count recent requests
        total_requests = sum(c for _, c in history)
        
        # Calculate reset time
        if history:
            reset_time = int(history[0][0] + window)
        else:
            reset_time = int(current_time + window)
        
        # Check if limit exceeded
        if total_requests >= max_requests:
            return False, {
                "remaining": 0,
                "limit": max_requests,
                "reset": reset_time,
                "retry_after": reset_time - int(current_time)
            }
        
        # Add current request
        history.append((current_time, 1))
        
        return True, {
            "remaining": max_requests - total_requests - 1,
            "limit": max_requests,
            "reset": reset_time
        }


class GranularRateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for granular rate limiting."""
    
    def __init__(self, app, limiter: Optional[GranularRateLimiter] = None):
        super().__init__(app)
        self.limiter = limiter or GranularRateLimiter()
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Determine endpoint type
        endpoint_type = self.limiter.get_endpoint_type(
            request.method,
            request.url.path
        )
        
        # Check rate limit
        allowed, info = self.limiter.is_allowed(client_ip, endpoint_type)
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "error": "Too many requests",
                    "retry_after": info.get("retry_after", 60)
                },
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info.get("retry_after", 60))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
        
        return response


# Create global limiter instance
rate_limiter = GranularRateLimiter()


def get_rate_limit_middleware():
    """Get rate limit middleware instance."""
    return GranularRateLimitMiddleware
