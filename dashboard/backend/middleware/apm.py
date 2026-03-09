"""
APM Middleware - Application Performance Monitoring

Provides comprehensive performance monitoring with Prometheus metrics:
- Response time histograms (p50, p95, p99)
- Throughput counters (requests/min)
- Error rate gauges
- Database query time tracking
- Cache hit/miss rates
- Active requests gauge
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge, Info
import structlog

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Number of active HTTP requests',
    ['method']
)

ERROR_RATE = Gauge(
    'http_error_rate',
    'HTTP error rate percentage',
    ['endpoint']
)

DB_QUERY_LATENCY = Histogram(
    'db_query_duration_seconds',
    'Database query latency in seconds',
    ['query_type'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

CACHE_HITS = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

APP_INFO = Info(
    'app_info',
    'Application information'
)


class APMMiddleware(BaseHTTPMiddleware):
    """
    APM Middleware for FastAPI
    
    Automatically tracks:
    - Request count by method, endpoint, status code
    - Request latency with histogram buckets
    - Active requests gauge
    - Error rates
    
    Usage:
        app.add_middleware(APMMiddleware)
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics"""
        
        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)
        
        method = request.method
        endpoint = self._get_endpoint_pattern(request)
        
        # Track active requests
        ACTIVE_REQUESTS.labels(method=method).inc()
        
        # Start timer
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            status_code = str(response.status_code)
            duration = time.time() - start_time
            
            # Update counters and histograms
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            # Track error rate (4xx and 5xx)
            if response.status_code >= 400:
                ERROR_RATE.labels(endpoint=endpoint).set(1)
            else:
                ERROR_RATE.labels(endpoint=endpoint).set(0)
            
            return response
            
        except Exception as e:
            # Record error
            duration = time.time() - start_time
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code='500'
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            ERROR_RATE.labels(endpoint=endpoint).set(1)
            
            logger.error(
                "Request failed",
                method=method,
                endpoint=endpoint,
                error=str(e),
                duration=duration
            )
            
            raise
            
        finally:
            # Decrement active requests
            ACTIVE_REQUESTS.labels(method=method).dec()
    
    def _get_endpoint_pattern(self, request: Request) -> str:
        """
        Extract endpoint pattern from request
        
        Converts /users/123 -> /users/{id}
        """
        path = request.url.path
        
        # Try to get route pattern from FastAPI app
        if hasattr(request.app, 'routes'):
            for route in request.app.routes:
                if hasattr(route, 'path') and hasattr(route, 'path_regex'):
                    if route.path_regex.match(path):
                        return route.path
        
        # Fallback to raw path if no pattern found
        return path


def track_db_query(query_type: str):
    """
    Decorator to track database query performance
    
    Usage:
        @track_db_query("select")
        async def get_user(user_id: int):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                DB_QUERY_LATENCY.labels(query_type=query_type).observe(duration)
        return wrapper
    return decorator


def track_cache_hit(cache_type: str):
    """Track cache hit"""
    CACHE_HITS.labels(cache_type=cache_type).inc()


def track_cache_miss(cache_type: str):
    """Track cache miss"""
    CACHE_MISSES.labels(cache_type=cache_type).inc()


def init_app_info(version: str = "0.1.0", environment: str = "development"):
    """Initialize application info metric"""
    APP_INFO.info({
        'version': version,
        'environment': environment
    })
