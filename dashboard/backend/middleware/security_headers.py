"""
Security Headers Middleware

Adds security headers to all responses:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Content-Security-Policy: default-src 'self'
- Strict-Transport-Security: max-age=31536000; includeSubDomains
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: restrictive defaults
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security headers middleware for FastAPI
    
    Adds security headers to all responses to protect against:
    - MIME type sniffing
    - Clickjacking
    - XSS attacks
    - Man-in-the-middle attacks
    - Information leakage
    
    Usage:
        app.add_middleware(SecurityHeadersMiddleware)
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response"""
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )
        
        # Content Security Policy (adjust based on your needs)
        # For API-only services, use restrictive CSP
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )
        
        # Remove server information
        if "Server" in response.headers:
            del response.headers["Server"]
        
        return response


def get_security_headers() -> dict:
    """Get all security headers as dict"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'",
        "Permissions-Policy": (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )
    }
