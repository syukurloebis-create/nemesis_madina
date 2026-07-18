# backend/telemetry/log_context.py

from contextvars import ContextVar
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from contextlib import contextmanager


class LogContext:
    """Log context for structured logging."""
    
    def __init__(self):
        self._context: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any):
        """Set context value."""
        self._context[key] = value
    
    def get(self, key: str) -> Optional[Any]:
        """Get context value."""
        return self._context.get(key)
    
    def update(self, **kwargs):
        """Update context with multiple values."""
        self._context.update(kwargs)
    
    def clear(self):
        """Clear context."""
        self._context.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Get context as dictionary."""
        return dict(self._context)


# Global context
log_context = LogContext()


@contextmanager
def log_context_scope(**kwargs):
    """Context manager for temporary log context."""
    old_context = dict(log_context._context)
    try:
        log_context.update(**kwargs)
        yield
    finally:
        log_context.clear()
        log_context.update(old_context)


def add_log_context(**kwargs):
    """Decorator for adding log context to functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            with log_context_scope(**kwargs):
                return await func(*args, **kwargs)
        return wrapper
    return decorator