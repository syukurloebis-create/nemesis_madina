"""API Middleware"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        print(f">>> {request.method} {request.url.path}")
        response = await call_next(request)
        duration = (time.perf_counter() - start) * 1000
        print(f"<<< {response.status_code} ({duration:.2f}ms)")
        response.headers["X-Response-Time-Ms"] = str(int(duration))
        return response


def setup_middleware(app):
    app.add_middleware(LoggingMiddleware)
    return app
