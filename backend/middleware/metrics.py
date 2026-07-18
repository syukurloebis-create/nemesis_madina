# backend/middleware/metrics.py

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from backend.telemetry.metrics import record_dashboard_request
from backend.telemetry.logging import generate_request_id, set_request_id


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for recording request metrics."""
    
    async def dispatch(self, request: Request, call_next):
        # Set request ID
        request_id = request.headers.get("X-Request-ID", generate_request_id())
        set_request_id(request_id)
        
        # Record start time
        start_time = time.perf_counter()
        
        # Process request
        response: Response = await call_next(request)
        
        # Record metrics
        duration = time.perf_counter() - start_time
        record_dashboard_request(
            duration_seconds=duration,
            status_code=response.status_code,
            endpoint=request.url.path
        )
        
        # Add request ID to response
        response.headers["X-Request-ID"] = request_id
        
        return response