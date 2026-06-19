from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import json
import logging

logger = logging.getLogger(__name__)


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware untuk validasi request body"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip validation for non-POST/PUT/PATCH
        if request.method not in ["POST", "PUT", "PATCH"]:
            return await call_next(request)
        
        # Skip validation for certain paths
        skip_paths = ["/health", "/metrics", "/ready", "/live"]
        if request.url.path in skip_paths:
            return await call_next(request)
        
        # Validate content type
        content_type = request.headers.get("content-type", "")
        if "application/json" not in content_type:
            return JSONResponse(
                status_code=415,
                content={"detail": "Content-Type must be application/json"}
            )
        
        # Validate JSON body
        try:
            body = await request.body()
            if body:
                json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return JSONResponse(
                status_code=400,
                content={"detail": f"Invalid JSON: {str(e)}"}
            )
        
        response = await call_next(request)
        return response


# Alias untuk backward compatibility
ValidationMiddleware = RequestValidationMiddleware