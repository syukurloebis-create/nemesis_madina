# backend/telemetry/logger_provider.py

from typing import Optional, Dict, Any
import logging
import json
from datetime import datetime, timezone


class LoggerProvider:
    """Provider for structured logging."""
    
    def __init__(self, service_name: str = "nemesis-dashboard"):
        self.service_name = service_name
        self._logger = logging.getLogger(service_name)
    
    async def startup(self):
        """Initialize logger."""
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter(self.service_name))
        self._logger.handlers = [handler]
        self._logger.setLevel(logging.INFO)
    
    async def shutdown(self):
        """Shutdown logger."""
        pass
    
    def log(self, message: str, level: str = "info", **kwargs):
        """Log a message with context."""
        extra = kwargs.get("extra", {})
        getattr(self._logger, level.lower())(message, extra=extra)
    
    def with_context(self, context: Dict[str, Any]):
        """Create logger with context."""
        return ContextLogger(self, context)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logs."""
    
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.service_name,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
        
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1])
            }
        
        return json.dumps(log_entry)


class ContextLogger:
    """Logger with pre-set context."""
    
    def __init__(self, provider: LoggerProvider, context: Dict[str, Any]):
        self._provider = provider
        self._context = context
    
    def log(self, message: str, level: str = "info", **kwargs):
        extra = kwargs.get("extra", {})
        extra.update(self._context)
        self._provider.log(message, level, extra=extra)
    
    def info(self, message: str, **kwargs):
        self.log(message, "info", **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log(message, "error", **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log(message, "warning", **kwargs)
    
    def debug(self, message: str, **kwargs):
        self.log(message, "debug", **kwargs)