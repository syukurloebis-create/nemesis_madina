"""
Tracing - Distributed Tracing Support
"""

import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from collections import defaultdict


class Span:
    """Single trace span"""
    
    def __init__(
        self,
        name: str,
        trace_id: str = None,
        parent_span_id: str = None,
        span_id: str = None
    ):
        self.name = name
        self.trace_id = trace_id or str(uuid.uuid4())
        self.span_id = span_id or str(uuid.uuid4())
        self.parent_span_id = parent_span_id
        self.start_time = time.perf_counter()
        self.end_time = None
        self.attributes: Dict[str, Any] = {}
        self.events: List[Dict[str, Any]] = []
        self.status = "ok"
    
    def set_attribute(self, key: str, value: Any):
        """Set span attribute"""
        self.attributes[key] = value
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """Add event to span"""
        self.events.append({
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "attributes": attributes or {}
        })
    
    def set_status(self, status: str):
        """Set span status"""
        self.status = status
    
    def end(self):
        """End the span"""
        self.end_time = time.perf_counter()
    
    @property
    def duration_ms(self) -> float:
        """Get span duration in milliseconds"""
        if self.end_time is None:
            return 0
        return (self.end_time - self.start_time) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
            "events": self.events,
            "status": self.status
        }


class Tracer:
    """Distributed tracer - Singleton"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._spans: List[Span] = []
        self._active_spans: List[Span] = []
        self._initialized = True
    
    def start_span(
        self,
        name: str,
        trace_id: str = None,
        parent_span_id: str = None
    ) -> Span:
        """Start a new span"""
        span = Span(name, trace_id, parent_span_id)
        self._active_spans.append(span)
        return span
    
    def end_span(self, span: Span):
        """End a span"""
        span.end()
        self._spans.append(span)
        if span in self._active_spans:
            self._active_spans.remove(span)
    
    @contextmanager
    def trace(self, name: str, attributes: Dict[str, Any] = None):
        """Context manager for tracing"""
        span = self.start_span(name)
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        
        try:
            yield span
            span.set_status("ok")
        except Exception as e:
            span.set_status("error")
            span.add_event("exception", {"error": str(e)})
            raise
        finally:
            self.end_span(span)
    
    def get_current_span(self) -> Optional[Span]:
        """Get current active span"""
        if self._active_spans:
            return self._active_spans[-1]
        return None
    
    def get_all_spans(self) -> List[Span]:
        """Get all completed spans"""
        return self._spans.copy()
    
    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for a trace"""
        return [s for s in self._spans if s.trace_id == trace_id]
    
    def get_traces(self, limit: int = 100) -> Dict[str, Any]:
        """Get recent traces summary"""
        traces = defaultdict(list)
        for span in self._spans[-limit:]:
            traces[span.trace_id].append(span.to_dict())
        
        return dict(traces)
    
    def clear(self):
        """Clear all spans"""
        self._spans.clear()
        self._active_spans.clear()


# Global tracer
tracer = Tracer()


def trace(name: str, attributes: Dict[str, Any] = None):
    """Decorator for tracing functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with tracer.trace(name or func.__name__, attributes):
                return func(*args, **kwargs)
        return wrapper
    return decorator
