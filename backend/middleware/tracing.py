"""
NEMESIS Madina - Tracing Middleware
✅ Trace context propagation for HTTP requests
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from backend.infrastructure.observability.opentelemetry_tracing import get_tracer
from backend.infrastructure.observability.tracing import SpanContext
import uuid


class TracingMiddleware(BaseHTTPMiddleware):
    """Tracing middleware for HTTP requests."""
    
    async def dispatch(self, request: Request, call_next):
        tracer = get_tracer()
        
        # Extract trace context from headers
        headers = dict(request.headers)
        span_context = tracer.extract_context(headers)
        
        # Create trace context for propagation
        trace_id = str(uuid.uuid4())
        
        # Start span
        with tracer.start_span(
            name=f"HTTP {request.method} {request.url.path}",
            span_type="server",
            parent_context=headers if span_context else None,
            attributes={
                "http.method": request.method,
                "http.url": str(request.url),
                "http.path": request.url.path,
                "http.client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        ):
            # Set correlation ID
            correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
            tracer.set_attribute("correlation_id", correlation_id)
            
            # Add correlation ID to response headers
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            
            # Record HTTP status
            tracer.set_attribute("http.status_code", response.status_code)
            
            if response.status_code >= 500:
                tracer.set_attribute("http.error", True)
            
            return response