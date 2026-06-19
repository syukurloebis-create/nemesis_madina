from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from backend.security.auth import decode_token
import logging

logger = logging.getLogger(__name__)

class RBACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Public endpoints
        public_paths = ["/health", "/metrics", "/docs", "/openapi.json", "/auth/login", "/auth/register", "/"]
        
        if any(request.url.path == path or request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        # Extract token
        auth_header = request.headers.get("Authorization")
        institution_id = None
        role = None
        user_id = None
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            logger.info(f"🔑 Processing token for {request.method} {request.url.path}")
            
            try:
                payload = decode_token(token)
                if payload:
                    institution_id = payload.get("institution_id")
                    role = payload.get("role")
                    user_id = payload.get("sub")
                    logger.info(f"✅ Institution: {institution_id}, Role: {role}")
                else:
                    logger.error("❌ Payload is None")
            except Exception as e:
                logger.error(f"❌ Error: {e}")
        else:
            logger.warning(f"⚠️ No Bearer token for {request.url.path}")
        
        # ALWAYS set to request.state
        request.state.institution_id = institution_id
        request.state.role = role
        request.state.user_id = user_id
        
        # ADMIN bypass
        if role == "ADMIN":
            logger.info("👑 ADMIN bypass")
            return await call_next(request)
        
        # Check institution for protected endpoints
        protected_endpoints = ["/cases", "/evidence", "/upload", "/entities", "/alerts", "/reports", "/vendors", "/findings"]
        
        if any(request.url.path.startswith(endpoint) for endpoint in protected_endpoints):
            if not institution_id:
                logger.error(f"❌ No institution_id for {request.url.path}")
                raise HTTPException(status_code=403, detail="No institution assigned")
            
            logger.info(f"✅ Access granted for institution: {institution_id}")
        
        return await call_next(request)
