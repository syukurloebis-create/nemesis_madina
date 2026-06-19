# backend/events/tracing.py
from contextvars import ContextVar
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# Context variables untuk distributed tracing
_current_correlation_id: ContextVar[Optional[uuid.UUID]] = ContextVar(
    'correlation_id', default=None
)
_current_causation_id: ContextVar[Optional[uuid.UUID]] = ContextVar(
    'causation_id', default=None
)


@dataclass
class TraceContext:
    """Tracing context untuk event chain"""
    correlation_id: uuid.UUID
    causation_id: Optional[uuid.UUID] = None
    parent_span_id: Optional[uuid.UUID] = None
    trace_depth: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def start_span(self, name: str) -> 'TraceContext':
        """Start child span"""
        return TraceContext(
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            parent_span_id=uuid.uuid4(),
            trace_depth=self.trace_depth + 1,
            metadata={"span_name": name, **self.metadata}
        )
    
    def end_span(self):
        """End current span (return to parent)"""
        return TraceContext(
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            parent_span_id=None,
            trace_depth=self.trace_depth - 1,
            metadata=self.metadata
        )


class TraceManager:
    """Manager untuk distributed tracing"""
    
    @staticmethod
    def start_trace() -> TraceContext:
        """Start new trace"""
        correlation_id = uuid.uuid4()
        ctx = TraceContext(correlation_id=correlation_id)
        _current_correlation_id.set(correlation_id)
        return ctx
    
    @staticmethod
    def continue_trace(correlation_id: uuid.UUID, causation_id: Optional[uuid.UUID] = None) -> TraceContext:
        """Continue existing trace"""
        ctx = TraceContext(
            correlation_id=correlation_id,
            causation_id=causation_id
        )
        _current_correlation_id.set(correlation_id)
        if causation_id:
            _current_causation_id.set(causation_id)
        return ctx
    
    @staticmethod
    def get_current_context() -> Optional[TraceContext]:
        """Get current trace context"""
        corr_id = _current_correlation_id.get()
        if not corr_id:
            return None
        return TraceContext(
            correlation_id=corr_id,
            causation_id=_current_causation_id.get()
        )
    
    @staticmethod
    def clear():
        """Clear current context"""
        _current_correlation_id.set(None)
        _current_causation_id.set(None)


class TraceMiddleware:
    """Middleware untuk tracing HTTP requests"""
    
    async def __call__(self, request, call_next):
        # Get or create correlation ID from header
        correlation_header = request.headers.get("X-Correlation-ID")
        
        if correlation_header:
            try:
                correlation_id = uuid.UUID(correlation_header)
                trace = TraceManager.continue_trace(correlation_id)
            except ValueError:
                trace = TraceManager.start_trace()
        else:
            trace = TraceManager.start_trace()
        
        # Add to request state
        request.state.trace = trace
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = str(trace.correlation_id)
        
        # Clear context
        TraceManager.clear()
        
        return response