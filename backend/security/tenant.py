"""
Multi-tenant Isolation Module
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import jwt


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    """Middleware untuk inject institution_id ke request state"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip untuk public endpoints
        public_paths = ["/health", "/metrics", "/api/v1/auth/login", "/docs", "/openapi.json", "/redoc"]
        if request.url.path in public_paths or request.url.path.startswith("/docs"):
            return await call_next(request)
        
        # Ambil token dari header
        auth_header = request.headers.get("Authorization")
        institution_id = None
        user_id = None
        role = None
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get("sub")
                role = payload.get("role")
                institution_id = payload.get("institution_id")
                
                # Jika institution_id tidak ada di token, coba dari database
                if not institution_id and user_id:
                    from sqlalchemy import select
                    from backend.infrastructure.database import AsyncSessionLocal
                    from backend.security.models import User
                    
                    async with AsyncSessionLocal() as session:
                        result = await session.execute(
                            select(User).where(User.id == user_id)
                        )
                        user = result.scalar_one_or_none()
                        if user:
                            institution_id = user.institution_id
                            role = user.role.value
                            
            except Exception as e:
                pass
        
        # Inject ke request state
        request.state.user_id = user_id
        request.state.role = role
        request.state.institution_id = institution_id
        
        # Validasi: endpoint yang butuh tenant harus punya institution_id
        if not institution_id and not request.url.path.startswith("/health"):
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing tenant context"
            )
        
        response = await call_next(request)
        return response


def get_current_tenant(request: Request) -> dict:
    """Get current tenant information from request state"""
    return {
        "institution_id": getattr(request.state, "institution_id", None),
        "user_id": getattr(request.state, "user_id", None),
        "role": getattr(request.state, "role", None),
    }


def get_current_institution_id(request: Request) -> Optional[str]:
    """Get current institution ID from request state"""
    return getattr(request.state, "institution_id", None)