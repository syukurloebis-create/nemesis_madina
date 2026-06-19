import time
from starlette.middleware.base import BaseHTTPMiddleware
from backend.telemetry.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware untuk mengumpulkan metrics HTTP request"""
    
    async def dispatch(self, request, call_next):
        method = request.method
        path = request.url.path
        
        # Increment in-progress counter
        http_requests_in_progress.labels(method=method).inc()
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            
            # Record request duration
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            # Increment total requests counter
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status=status_code
            ).inc()
            
            # Decrement in-progress counter
            http_requests_in_progress.labels(method=method).dec()
        
        return response