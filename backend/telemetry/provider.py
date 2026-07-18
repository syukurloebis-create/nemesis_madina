# backend/telemetry/provider.py

from typing import Protocol, Optional, Any, Dict
from backend.telemetry.metrics_registry import MetricsRegistry
from backend.telemetry.tracer_provider import TracerProvider
from backend.telemetry.logger_provider import LoggerProvider


class TelemetryProvider:
    """
    Telemetry provider - abstraction for all observability.
    
    Provides:
    - Metrics
    - Tracing
    - Logging
    - Context propagation
    """
    
    def __init__(
        self,
        metrics: Optional[MetricsRegistry] = None,
        tracer: Optional[TracerProvider] = None,
        logger: Optional[LoggerProvider] = None
    ):
        self.metrics = metrics or MetricsRegistry()
        self.tracer = tracer or TracerProvider()
        self.logger = logger or LoggerProvider()
    
    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a metric."""
        self.metrics.record(name, value, labels)
    
    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Start a trace span."""
        return self.tracer.start_span(name, attributes)
    
    def log(self, message: str, level: str = "info", **kwargs):
        """Log a message with context."""
        self.logger.log(message, level, **kwargs)
    
    async def startup(self):
        """Initialize telemetry."""
        await self.metrics.startup()
        await self.tracer.startup()
        await self.logger.startup()
    
    async def shutdown(self):
        """Shutdown telemetry."""
        await self.metrics.shutdown()
        await self.tracer.shutdown()
        await self.logger.shutdown()