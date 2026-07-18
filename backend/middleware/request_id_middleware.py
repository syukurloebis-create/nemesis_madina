"""
Request ID Middleware
Memberikan ID unik untuk setiap request.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.core.context import set_request_id, generate_request_id, get_request_id

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware yang menambahkan Request ID ke setiap request.
    """

    async def dispatch(self, request: Request, call_next):
        # Ambil dari header atau buat baru
        request_id = request.headers.get(REQUEST_ID_HEADER)
        if not request_id:
            request_id = generate_request_id()

        # Set di context
        set_request_id(request_id)

        # Proses request
        response = await call_next(request)

        # Tambahkan ke response header
        response.headers[REQUEST_ID_HEADER] = request_id

        return response


# Alias untuk kompatibilitas dengan nama lama
CorrelationIDMiddleware = RequestIDMiddleware