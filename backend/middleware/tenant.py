# backend/middleware/tenant.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """Multi-tenant enforcement middleware"""
    
    PUBLIC_PATHS = {
        "/health",
        "/metrics",
        "/openapi.json",
        "/docs",
        "/redoc",
        "/auth/login",
        "/auth/refresh",
        "/"
    }
    
    async def dispatch(self, request: Request, call_next):
        # Skip public paths
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)
        
        # Extract tenant from header
        tenant_id = request.headers.get("X-Tenant-ID")
        
        # If not in header, try to get from JWT
        if not tenant_id:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
                tenant_id = await self._extract_tenant_from_token(token)
        
        if not tenant_id:
            raise HTTPException(
                status_code=401,
                detail="Missing tenant ID. Provide X-Tenant-ID header."
            )
        
        # Validate UUID format
        try:
            uuid.UUID(tenant_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tenant ID format")
        
        # Store in request state
        request.state.tenant_id = tenant_id
        
        # Log tenant context
        logger.debug(f"Tenant: {tenant_id} - {request.method} {request.url.path}")
        
        response = await call_next(request)
        return response
    
    async def _extract_tenant_from_token(self, token: str) -> Optional[str]:
        """Extract tenant from JWT token"""
        try:
            from security.auth import AuthService
            payload = AuthService.decode_token(token)
            return payload.get("tenant_id")
        except Exception:
            return None