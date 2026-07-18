"""
Correlation ID Middleware
Memberikan ID unik untuk setiap request yang dibawa lintas service.
"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware yang menambahkan Correlation ID ke setiap request.
    """

    async def dispatch(self, request: Request, call_next):
        # Ambil dari header atau buat baru
        correlation_id = request.headers.get(CORRELATION_ID_HEADER)
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Simpan di request state untuk diakses service
        request.state.correlation_id = correlation_id

        # Tambahkan ke logger
        import logging
        logger = logging.getLogger(__name__)
        logger = logging.LoggerAdapter(logger, {"correlation_id": correlation_id})

        # Proses request
        response = await call_next(request)

        # Tambahkan ke response header
        response.headers[CORRELATION_ID_HEADER] = correlation_id

        return response