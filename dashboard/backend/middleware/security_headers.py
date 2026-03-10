"""
Security Headers Middleware for QA-FRAMEWORK.

Adds essential security headers to all responses to protect against
common web vulnerabilities (XSS, clickjacking, MIME sniffing, etc.)
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all HTTP responses.
    
    Headers added:
    - X-Frame-Options: Prevents clickjacking
    - X-Content-Type-Options: Prevents MIME sniffing
    - Strict-Transport-Security: Forces HTTPS
    - X-XSS-Protection: XSS filter (legacy but still useful)
    - Content-Security-Policy: Prevents XSS and injection attacks
    - Referrer-Policy: Controls referrer information
    - Permissions-Policy: Restricts browser features
    """
    
    async def dispatch(self, request: Request, call_next):
        # Call next middleware/route handler
        response: Response = await call_next(request)
        
        # Add security headers
        headers = {
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Force HTTPS (1 year, include subdomains)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # XSS Protection (legacy but still useful for older browsers)
            "X-XSS-Protection": "1; mode=block",
            
            # Control referrer information
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Restrict browser features
            "Permissions-Policy": (
                "accelerometer=(), "
                "camera=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "microphone=(), "
                "payment=(), "
                "usb=()"
            ),
            
            # Content Security Policy (restrictive but functional)
            # Note: Adjust as needed for your application
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # unsafe-inline needed for inline scripts
                "style-src 'self' 'unsafe-inline'; "  # unsafe-inline needed for inline styles
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https:; "  # Allow HTTPS API calls
                "frame-ancestors 'none'; "  # Equivalent to X-Frame-Options: DENY
                "base-uri 'self'; "
                "form-action 'self'"
            ),
        }
        
        # Add headers to response
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value
        
        return response


# Alternative: Function to add headers manually if middleware is not desired
def add_security_headers(response: Response) -> Response:
    """
    Manually add security headers to a response.
    Use this if you can't use middleware for some reason.
    """
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
        "magnetometer=(), microphone=(), payment=(), usb=()"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    return response
