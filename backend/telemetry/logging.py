# backend/telemetry/logging.py

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import uuid4
from contextvars import ContextVar

request_id_var = ContextVar("request_id", default=None)

class StructuredLogging:
    """Structured logging with JSON format."""
    
    def __init__(self, service_name: str = "nemesis-dashboard"):
        self.service_name = service_name
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup structured logging."""
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter(self.service_name))
        
        logger = logging.getLogger()
        logger.handlers = []
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get structured logger."""
        return logging.getLogger(name)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logs."""
    
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.service_name,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
        
        # Add exception info
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        return json.dumps(log_entry)


# Global logger
logger = StructuredLogging().get_logger(__name__)


def log_with_context(message: str, level: str = "info", **kwargs):
    """Log with context."""
    extra = kwargs.get("extra", {})
    extra["request_id"] = request_id_var.get()
    getattr(logger, level.lower())(message, extra=extra)


def set_request_id(request_id: str):
    """Set current request ID."""
    request_id_var.set(request_id)


def generate_request_id() -> str:
    """Generate a new request ID."""
    return str(uuid4())