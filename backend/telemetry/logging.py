"""
Logging - Structured Logging with JSON format
"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar


# Context variables for tracing
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
span_id_var: ContextVar[Optional[str]] = ContextVar('span_id', default=None)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add trace context
        trace_id = trace_id_var.get()
        if trace_id:
            log_entry["trace_id"] = trace_id
        
        span_id = span_id_var.get()
        if span_id:
            log_entry["span_id"] = span_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_entry["extra"] = record.extra_data
        
        return json.dumps(log_entry, default=str)


class StructuredLogger:
    """Structured logger with context support"""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(f"logs/{name}.log")
        file_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(file_handler)
    
    def _log(self, level: int, msg: str, **kwargs):
        """Internal log method with extra data"""
        extra = kwargs.pop('extra', {})
        if extra:
            # Create a log record with extra data
            self.logger.log(level, msg, extra={'extra_data': extra})
        else:
            self.logger.log(level, msg)
    
    def debug(self, msg: str, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)
    
    def info(self, msg: str, **kwargs):
        self._log(logging.INFO, msg, **kwargs)
    
    def warning(self, msg: str, **kwargs):
        self._log(logging.WARNING, msg, **kwargs)
    
    def error(self, msg: str, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)
    
    def critical(self, msg: str, **kwargs):
        self._log(logging.CRITICAL, msg, **kwargs)
    
    def exception(self, msg: str, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(msg, extra={'extra_data': kwargs})


# Default logger
default_logger = StructuredLogger("nemesis")


def get_logger(name: str = None) -> StructuredLogger:
    """Get logger instance"""
    if name:
        return StructuredLogger(name)
    return default_logger


def set_trace_context(trace_id: str, span_id: str = None):
    """Set trace context for current execution"""
    trace_id_var.set(trace_id)
    if span_id:
        span_id_var.set(span_id)


def clear_trace_context():
    """Clear trace context"""
    trace_id_var.set(None)
    span_id_var.set(None)
