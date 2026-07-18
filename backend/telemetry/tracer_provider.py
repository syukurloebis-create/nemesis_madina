# backend/telemetry/tracer_provider.py

from typing import Optional, Dict, Any, AsyncContextManager
from contextlib import asynccontextmanager
from opentelemetry import trace
from opentelemetry.trace import Span, Tracer


class TracerProvider:
    """Provider for tracing."""
    
    def __init__(self, service_name: str = "nemesis-dashboard"):
        self.service_name = service_name
        self._tracer: Optional[Tracer] = None
    
    async def startup(self):
        """Initialize tracer."""
        from opentelemetry.sdk.trace import TracerProvider as SDKProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        
        provider = SDKProvider()
        trace.set_tracer_provider(provider)
        self._tracer = trace.get_tracer(self.service_name)
    
    async def shutdown(self):
        """Shutdown tracer."""
        trace.set_tracer_provider(None)
    
    def get_tracer(self) -> Optional[Tracer]:
        """Get tracer instance."""
        return self._tracer or trace.get_tracer(self.service_name)
    
    @asynccontextmanager
    async def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Start a span."""
        tracer = self.get_tracer()
        with tracer.start_as_current_span(name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            yield span