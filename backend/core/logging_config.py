"""
Logging configuration with JSON formatter untuk observability.
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any
from backend.core.context import get_request_id


class JSONFormatter(logging.Formatter):
    """
    JSON formatter untuk structured logging.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "request_id": get_request_id() or "N/A",
        }

        # Tambahkan exception info jika ada
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "stack": self.formatException(record.exc_info)
            }

        # Tambahkan extra fields
        if hasattr(record, "extra"):
            log_entry["extra"] = record.extra

        return json.dumps(log_entry, default=str)


def setup_logging():
    """Setup structured logging."""
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Hapus handler default
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler dengan JSON formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)

    # Set level untuk library
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return root_logger