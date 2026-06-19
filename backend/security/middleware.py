"""
Authentication Middleware
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import os
from jose import JWTError

# List of public endpoints (no auth required)
PUBLIC_ENDPOINTS = [
    "/health",
    "/docs",
    "/openapi.json",
    "/auth/login",
    "/auth/register",
    "/api/auth/login",
    "/api/auth/register"
]

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        path = request.url.path
        if path in PUBLIC_ENDPOINTS or path.startswith("/auth") or path.startswith("/docs"):
            return await call_next(request)
        
        # Check for token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid authentication token"}
            )
        
        token = auth_header.split(" ")[1]
        try:
            # Validate token (will be done in endpoint)
            request.state.token = token
            return await call_next(request)
        except JWTError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"}
            )
