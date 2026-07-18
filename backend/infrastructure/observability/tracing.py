"""
NEMESIS Madina - Tracing Interface
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, ContextManager


class SpanContext:
    """Trace span context."""
    
    def __init__(
        self,
        trace_id: str,
        span_id: str,
        trace_flags: int = 0,
    ):
        self.trace_id = trace_id
        self.span_id = span_id
        self.trace_flags = trace_flags


class ITracer(ABC):
    """Tracer interface."""
    
    @abstractmethod
    def start_span(
        self,
        name: str,
        span_type: str = "internal",
        parent_context: Optional[Dict[str, str]] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> ContextManager:
        """Start a new span."""
        pass
    
    @abstractmethod
    def inject_context(self, span_context: SpanContext, carrier: Dict[str, str]) -> None:
        """Inject trace context into carrier."""
        pass
    
    @abstractmethod
    def extract_context(self, carrier: Dict[str, str]) -> Optional[SpanContext]:
        """Extract trace context from carrier."""
        pass
    
    @abstractmethod
    def set_attribute(self, key: str, value: Any) -> None:
        """Set attribute on current span."""
        pass
    
    @abstractmethod
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add event to current span."""
        pass
    
    @abstractmethod
    def record_exception(self, exception: Exception) -> None:
        """Record exception on current span."""
        pass
    
    @abstractmethod
    def set_ok(self) -> None:
        """Set current span as OK."""
        pass


class NoopTracer(ITracer):
    """No-op tracer for development."""
    
    def start_span(self, name: str, span_type: str = "internal", 
                   parent_context: Optional[Dict[str, str]] = None,
                   attributes: Optional[Dict[str, Any]] = None) -> ContextManager:
        from contextlib import contextmanager
        @contextmanager
        def noop_span():
            yield
        return noop_span()
    
    def inject_context(self, span_context: SpanContext, carrier: Dict[str, str]) -> None:
        pass
    
    def extract_context(self, carrier: Dict[str, str]) -> Optional[SpanContext]:
        return None
    
    def set_attribute(self, key: str, value: Any) -> None:
        pass
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        pass
    
    def record_exception(self, exception: Exception) -> None:
        pass
    
    def set_ok(self) -> None:
        pass