from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class AuditMiddleware(BaseHTTPMiddleware):
    """Audit logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get request context
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        tenant_id = getattr(request.state, 'tenant_id', None)
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log audit entry (async to avoid blocking)
        await self._log_audit(
            method=method,
            path=path,
            status_code=response.status_code,
            client_ip=client_ip,
            user_agent=user_agent,
            tenant_id=tenant_id,
            duration_ms=duration_ms
        )
        
        # Add audit headers for debugging
        response.headers["X-Request-Duration-MS"] = str(int(duration_ms))
        
        return response
    
    async def _log_audit(
        self,
        method: str,
        path: str,
        status_code: int,
        client_ip: str,
        user_agent: str,
        tenant_id: Optional[str],
        duration_ms: float
    ):
        """Log audit entry (simplified - would write to database in production)"""
        # In production, this would write to audit_logs table
        logger.info(
            f"AUDIT: {method} {path} | status={status_code} | "
            f"ip={client_ip} | tenant={tenant_id} | duration={duration_ms:.2f}ms | "
            f"ua={user_agent[:50]}"
        )