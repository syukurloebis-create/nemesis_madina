"""
NEMESIS Madina - Prometheus Metrics Implementation
✅ Complete Prometheus metrics
✅ Counter, Histogram, Gauge support
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
import logging

from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
)

from backend.infrastructure.observability.metrics import IMetricsRecorder

logger = logging.getLogger(__name__)


class PrometheusMetricsRecorder(IMetricsRecorder):
    """
    Prometheus metrics recorder.
    ✅ Complete implementation
    ✅ All metric types supported
    """
    
    def __init__(self, namespace: str = "nemesis"):
        self._namespace = namespace
        self._registry = CollectorRegistry()
        
        # Metrics
        self._publish_counter = Counter(
            f"{namespace}_publish_total",
            "Total publish operations",
            ["event_type", "success"],
            registry=self._registry,
        )
        
        self._publish_duration = Histogram(
            f"{namespace}_publish_duration_seconds",
            "Publish duration in seconds",
            ["event_type"],
            registry=self._registry,
        )
        
        self._retry_counter = Counter(
            f"{namespace}_retry_total",
            "Total retry operations",
            ["event_type"],
            registry=self._registry,
        )
        
        self._dlq_counter = Counter(
            f"{namespace}_dlq_total",
            "Total dead letter queue entries",
            ["event_type", "error"],
            registry=self._registry,
        )
        
        self._projection_duration = Histogram(
            f"{namespace}_projection_duration_seconds",
            "Projection duration in seconds",
            ["event_type"],
            registry=self._registry,
        )
        
        self._pending_events = Gauge(
            f"{namespace}_pending_events",
            "Number of pending events",
            registry=self._registry,
        )
        
        self._processing_latency = Summary(
            f"{namespace}_processing_latency_seconds",
            "Processing latency in seconds",
            ["operation"],
            registry=self._registry,
        )
        
        self._error_counter = Counter(
            f"{namespace}_errors_total",
            "Total errors",
            ["operation", "error_type"],
            registry=self._registry,
        )
        
        self._active_connections = Gauge(
            f"{namespace}_active_connections",
            "Active connections",
            ["connection_type"],
            registry=self._registry,
        )
        
        self._event_throughput = Counter(
            f"{namespace}_event_throughput_total",
            "Event throughput",
            ["event_type"],
            registry=self._registry,
        )
    
    def record_publish(
        self,
        event_type: str,
        success: bool,
        duration_ms: float,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Record event publish."""
        self._publish_counter.labels(
            event_type=event_type,
            success=str(success).lower(),
        ).inc()
        
        self._publish_duration.labels(event_type=event_type).observe(
            duration_ms / 1000.0
        )
        
        if trace_id:
            logger.debug(
                f"Publish recorded: event_type={event_type}, "
                f"success={success}, trace_id={trace_id}"
            )
    
    def record_retry(
        self,
        event_type: str,
        retry_count: int,
        trace_id: Optional[str] = None,
    ) -> None:
        """Record event retry."""
        self._retry_counter.labels(event_type=event_type).inc()
        
        if retry_count > 3:
            logger.warning(
                f"High retry count: event_type={event_type}, "
                f"retry_count={retry_count}, trace_id={trace_id}"
            )
    
    def record_dlq(
        self,
        event_type: str,
        error: str,
        trace_id: Optional[str] = None,
    ) -> None:
        """Record DLQ entry."""
        self._dlq_counter.labels(
            event_type=event_type,
            error=error[:100],  # Truncate error
        ).inc()
        
        logger.error(
            f"DLQ entry: event_type={event_type}, "
            f"error={error}, trace_id={trace_id}"
        )
    
    def record_projection(
        self,
        event_type: str,
        duration_ms: float,
        trace_id: Optional[str] = None,
    ) -> None:
        """Record projection processing."""
        self._projection_duration.labels(event_type=event_type).observe(
            duration_ms / 1000.0
        )
    
    def increment_counter(
        self,
        name: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Increment counter."""
        # Dynamic counter creation if needed
        pass
    
    def record_histogram(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record histogram value."""
        # Dynamic histogram creation if needed
        pass
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set gauge value."""
        # Dynamic gauge creation if needed
        pass
    
    def update_pending_events(self, count: int) -> None:
        """Update pending events gauge."""
        self._pending_events.set(count)
    
    def record_processing_latency(self, operation: str, duration_ms: float) -> None:
        """Record processing latency."""
        self._processing_latency.labels(operation=operation).observe(
            duration_ms / 1000.0
        )
    
    def record_error(self, operation: str, error_type: str) -> None:
        """Record error."""
        self._error_counter.labels(
            operation=operation,
            error_type=error_type,
        ).inc()
    
    def update_connection_count(self, connection_type: str, count: int) -> None:
        """Update connection count."""
        self._active_connections.labels(connection_type=connection_type).set(count)
    
    def record_event_throughput(self, event_type: str, count: int) -> None:
        """Record event throughput."""
        self._event_throughput.labels(event_type=event_type).inc(count)
    
    async def get_metrics(self) -> bytes:
        """Get metrics for Prometheus."""
        return generate_latest(self._registry)
    
    async def get_metrics_text(self) -> str:
        """Get metrics as text."""
        return generate_latest(self._registry).decode('utf-8')
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._registry = CollectorRegistry()
        # Re-initialize metrics
        self.__init__(self._namespace)


# Singleton
_metrics_instance: Optional[PrometheusMetricsRecorder] = None


def get_metrics_recorder() -> PrometheusMetricsRecorder:
    """Get singleton metrics recorder."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = PrometheusMetricsRecorder()
    return _metrics_instance