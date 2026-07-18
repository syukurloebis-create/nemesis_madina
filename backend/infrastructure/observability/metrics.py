"""
NEMESIS Madina - Observability Metrics
✅ Metrics collection for Domain operations
✅ Collector performance tracking
✅ Outbox monitoring
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """Individual metric."""
    name: str
    value: float
    type: MetricType
    unit: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None


@dataclass
class MetricRegistry:
    """Registry for collecting metrics."""
    
    _metrics: List[Metric] = field(default_factory=list)
    
    def counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a counter metric."""
        self.record(name, value, MetricType.COUNTER, "count", tags)
    
    def gauge(self, name: str, value: float, unit: str = "value", tags: Optional[Dict[str, str]] = None) -> None:
        """Record a gauge metric."""
        self.record(name, value, MetricType.GAUGE, unit, tags)
    
    def timer(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a timer metric."""
        self.record(name, duration_ms, MetricType.TIMER, "ms", tags)
    
    def record(
        self,
        name: str,
        value: float,
        type: MetricType,
        unit: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a metric."""
        metric = Metric(
            name=name,
            value=value,
            type=type,
            unit=unit,
            tags=tags or {},
        )
        self._metrics.append(metric)
    
    def get_metrics(self, name: Optional[str] = None) -> List[Metric]:
        """Get metrics by name."""
        if name:
            return [m for m in self._metrics if m.name == name]
        return self._metrics.copy()
    
    def clear(self) -> None:
        """Clear all metrics."""
        self._metrics.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dict."""
        return {
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "type": m.type.value,
                    "unit": m.unit,
                    "timestamp": m.timestamp.isoformat(),
                    "tags": m.tags,
                    "description": m.description,
                }
                for m in self._metrics
            ]
        }
    
    def __len__(self) -> int:
        return len(self._metrics)


# Global registry
default_registry = MetricRegistry()


def record_aggregate_operation(
    operation: str,
    aggregate_type: str,
    duration_ms: float,
    events_count: int,
    success: bool,
) -> None:
    """Record aggregate operation metrics."""
    tags = {
        "aggregate_type": aggregate_type,
        "operation": operation,
        "success": str(success).lower(),
    }
    
    default_registry.timer(f"aggregate.{operation}.duration", duration_ms, tags)
    default_registry.counter(f"aggregate.{operation}.events", events_count, tags)
    default_registry.counter(f"aggregate.{operation}.total", 1.0, tags)


def record_repository_operation(
    operation: str,
    entity_type: str,
    duration_ms: float,
    success: bool,
    conflict: bool = False,
) -> None:
    """Record repository operation metrics."""
    tags = {
        "entity_type": entity_type,
        "operation": operation,
        "success": str(success).lower(),
        "conflict": str(conflict).lower(),
    }
    
    default_registry.timer(f"repository.{operation}.duration", duration_ms, tags)
    default_registry.counter(f"repository.{operation}.total", 1.0, tags)


def record_outbox_operation(
    operation: str,
    batch_size: int,
    success: bool,
    retry: bool = False,
) -> None:
    """Record outbox operation metrics."""
    tags = {
        "operation": operation,
        "success": str(success).lower(),
        "retry": str(retry).lower(),
    }
    
    default_registry.counter(f"outbox.{operation}.total", 1.0, tags)
    default_registry.gauge(f"outbox.{operation}.batch_size", batch_size, "count", tags)


def record_collector_performance(
    collector_name: str,
    duration_ms: float,
    rows_returned: int,
    success: bool,
) -> None:
    """Record collector performance metrics."""
    tags = {
        "collector": collector_name,
        "success": str(success).lower(),
    }
    
    default_registry.timer(f"collector.{collector_name}.duration", duration_ms, tags)
    default_registry.counter(f"collector.{collector_name}.rows", rows_returned, tags)