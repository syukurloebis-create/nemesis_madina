# backend/middleware/canonical_tenant.py

"""
Canonical Tenant Middleware - SEC-7.6 Phase 9

Enforces tenant context for all authenticated requests.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import uuid
import logging

from backend.services.jwt_service import JWTService

logger = logging.getLogger(__name__)


class CanonicalTenantMiddleware(BaseHTTPMiddleware):
    """
    Canonical multi-tenant enforcement middleware.

    SEC-7.6 Contract:
        - tenant_id comes from JWT (NOT X-Tenant-ID)
        - Missing tenant → HTTP 403
        - Invalid tenant → HTTP 403
        - Public paths are exempt
    """

    PUBLIC_PATHS = {
        "/health",
        "/health/dashboard",
        "/metrics",
        "/openapi.json",
        "/docs",
        "/redoc",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
        "/"
    }

    async def dispatch(self, request: Request, call_next):
        # Skip public paths
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)

        # Extract tenant from JWT
        tenant_id = await self._extract_tenant_from_token(request)

        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Missing tenant context"
            )

        # Validate UUID format
        try:
            uuid.UUID(tenant_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid tenant ID format"
            )

        # Store in request state
        request.state.tenant_id = tenant_id

        logger.debug(f"Tenant: {tenant_id} - {request.method} {request.url.path}")

        response = await call_next(request)
        return response

    async def _extract_tenant_from_token(self, request: Request) -> Optional[str]:
        """Extract tenant_id from JWT token."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header[7:]
        try:
            payload = JWTService.verify_access_token(token)
            return payload.get("tenant_id")
        except Exception:
            return None