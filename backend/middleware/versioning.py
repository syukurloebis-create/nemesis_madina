"""
Versioning Middleware

Adds version information to response headers.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.core.version import VersionInfo


class VersionMiddleware(BaseHTTPMiddleware):
    """Add version headers to all responses."""

    def __init__(self, app, version_info: VersionInfo):
        super().__init__(app)
        self._version_info = version_info

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-API-Version"] = self._version_info.api_version
        response.headers["X-Build-Version"] = self._version_info.build
        return response
