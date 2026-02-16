"""
Rate Limiting Middleware

Provides rate limiting functionality to protect against abuse.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Callable

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)


def setup_rate_limiting(app):
    """Setup rate limiting middleware for the FastAPI app"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Rate limit decorators for different endpoints
def rate_limit_login():
    """Rate limit for login attempts - 5 per minute"""
    return limiter.limit("5/minute")

def rate_limit_api():
    """Rate limit for API calls - 100 per minute"""
    return limiter.limit("100/minute")

def rate_limit_execution():
    """Rate limit for test execution - 10 per minute"""
    return limiter.limit("10/minute")