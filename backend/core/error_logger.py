"""
Logger untuk exception dengan klasifikasi.
"""

import logging
from typing import Optional

from backend.core.context import get_request_id
from backend.core.exceptions import ERROR_TYPE_MAP


def log_exception(
    logger: logging.Logger,
    exception: Exception,
    context: Optional[dict] = None,
    level: str = "error"
):
    """
    Log exception dengan klasifikasi dan context.

    Args:
        logger: Logger instance
        exception: Exception yang terjadi
        context: Context tambahan (case_id, finding_id, dll)
        level: Log level ('error', 'warning', 'info')
    """
    request_id = get_request_id() or "N/A"

    # Tentukan tipe error
    error_type = ERROR_TYPE_MAP.get(type(exception), "UNKNOWN")

    # Build log message
    log_data = {
        "request_id": request_id,
        "error_type": error_type,
        "error_class": exception.__class__.__name__,
        "error_message": str(exception),
        "context": context or {}
    }

    # Log sesuai level
    log_message = f"[ERROR:{error_type}] {exception.__class__.__name__}: {exception}"

    if level == "error":
        logger.error(log_message, extra=log_data, exc_info=True)
    elif level == "warning":
        logger.warning(log_message, extra=log_data)
    else:
        logger.info(log_message, extra=log_data)