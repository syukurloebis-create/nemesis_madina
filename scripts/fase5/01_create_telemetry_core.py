#!/usr/bin/env python3
"""
NEMESIS FASE 5 - Create Telemetry Core (Metrics, Logging, Tracing)
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

TELEMETRY_DIR = PROJECT_ROOT / "backend" / "telemetry"

def create_enhanced_metrics():
    """Create enhanced metrics.py with Prometheus support"""
    print("\n[1/6] Creating enhanced metrics...")
    
    content = '''"""
Metrics - Prometheus Metrics Collection
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import time
import threading


@dataclass
class Metric:
    """Single metric definition"""
    name: str
    type: str  # counter, gauge, histogram, summary
    description: str
    labels: Dict[str, str] = field(default_factory=dict)
    value: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsRegistry:
    """Central metrics registry - Singleton"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._metrics: Dict[str, Metric] = {}
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._initialized = True
    
    def counter(self, name: str, description: str = "", value: float = 1.0) -> float:
        """Increment counter"""
        self._counters[name] += value
        self._metrics[name] = Metric(
            name=name,
            type="counter",
            description=description,
            value=self._counters[name]
        )
        return self._counters[name]
    
    def gauge(self, name: str, value: float, description: str = "") -> float:
        """Set gauge value"""
        self._gauges[name] = value
        self._metrics[name] = Metric(
            name=name,
            type="gauge",
            description=description,
            value=value
        )
        return value
    
    def histogram(self, name: str, value: float, description: str = "") -> None:
        """Add value to histogram"""
        self._histograms[name].append(value)
        # Keep only last 1000 values
        if len(self._histograms[name]) > 1000:
            self._histograms[name] = self._histograms[name][-1000:]
    
    def get_counter(self, name: str) -> float:
        """Get counter value"""
        return self._counters.get(name, 0.0)
    
    def get_gauge(self, name: str) -> float:
        """Get gauge value"""
        return self._gauges.get(name, 0.0)
    
    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Get histogram statistics"""
        values = self._histograms.get(name, [])
        if not values:
            return {"count": 0, "sum": 0, "min": 0, "max": 0, "avg": 0}
        
        import numpy as np
        return {
            "count": len(values),
            "sum": float(np.sum(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "avg": float(np.mean(values)),
            "p50": float(np.percentile(values, 50)),
            "p90": float(np.percentile(values, 90)),
            "p95": float(np.percentile(values, 95)),
            "p99": float(np.percentile(values, 99))
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        metrics = {}
        
        # Counters
        for name, value in self._counters.items():
            metrics[name] = {"type": "counter", "value": value}
        
        # Gauges
        for name, value in self._gauges.items():
            metrics[name] = {"type": "gauge", "value": value}
        
        # Histograms
        for name in self._histograms:
            metrics[name] = {
                "type": "histogram",
                "stats": self.get_histogram_stats(name)
            }
        
        return metrics
    
    def reset(self):
        """Reset all metrics"""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._metrics.clear()
    
    def get_prometheus_format(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        for name, value in self._counters.items():
            lines.append(f"# HELP {name} Counter metric")
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value}")
        
        for name, value in self._gauges.items():
            lines.append(f"# HELP {name} Gauge metric")
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")
        
        for name, stats in self._histograms.items():
            hist_stats = self.get_histogram_stats(name)
            lines.append(f"# HELP {name} Histogram metric")
            lines.append(f"# TYPE {name} histogram")
            lines.append(f"{name}_count {hist_stats['count']}")
            lines.append(f"{name}_sum {hist_stats['sum']}")
        
        return "\\n".join(lines)


# Global registry
metrics_registry = MetricsRegistry()


# Convenience functions
def counter_inc(name: str, value: float = 1.0) -> float:
    """Increment counter metric"""
    return metrics_registry.counter(name, value=value)


def gauge_set(name: str, value: float) -> float:
    """Set gauge metric"""
    return metrics_registry.gauge(name, value)


def histogram_observe(name: str, value: float) -> None:
    """Observe histogram value"""
    metrics_registry.histogram(name, value)


def timed_metric(metric_name: str):
    """Decorator to measure function execution time"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                duration = (time.perf_counter() - start) * 1000
                histogram_observe(metric_name, duration)
                return result
            except Exception as e:
                counter_inc(f"{metric_name}_errors", 1)
                raise
        return wrapper
    return decorator


class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, metric_name: str):
        self.metric_name = metric_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        duration = (time.perf_counter() - self.start_time) * 1000
        histogram_observe(self.metric_name, duration)
'''
    
    file_path = TELEMETRY_DIR / "metrics.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_enhanced_logging():
    """Create enhanced logging.py with structured logging"""
    print("\n[2/6] Creating enhanced logging...")
    
    content = '''"""
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
'''
    
    file_path = TELEMETRY_DIR / "logging.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_tracing():
    """Create tracing.py for distributed tracing"""
    print("\n[3/6] Creating tracing...")
    
    content = '''"""
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
'''
    
    file_path = TELEMETRY_DIR / "tracing.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_dashboard():
    """Create dashboard.py for metrics dashboard"""
    print("\n[4/6] Creating dashboard...")
    
    content = '''"""
Dashboard - Metrics Dashboard API
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from backend.telemetry.metrics import metrics_registry


class MetricsDashboard:
    """Metrics dashboard for visualization"""
    
    def __init__(self):
        self.registry = metrics_registry
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": self._get_uptime(),
            "metrics": self.get_metrics_summary()
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        all_metrics = self.registry.get_all_metrics()
        
        summary = {
            "counters": {},
            "gauges": {},
            "histograms": {}
        }
        
        for name, metric in all_metrics.items():
            if metric["type"] == "counter":
                summary["counters"][name] = metric["value"]
            elif metric["type"] == "gauge":
                summary["gauges"][name] = metric["value"]
            elif metric["type"] == "histogram":
                summary["histograms"][name] = metric["stats"]
        
        return summary
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance-related metrics"""
        all_metrics = self.registry.get_all_metrics()
        
        performance = {
            "event_processing": {
                "avg_ms": 0,
                "p95_ms": 0,
                "total": 0
            },
            "api_latency": {
                "avg_ms": 0,
                "p95_ms": 0
            },
            "websocket": {
                "connections": 0,
                "messages_per_sec": 0
            }
        }
        
        # Extract from histograms
        for name, metric in all_metrics.items():
            if metric["type"] == "histogram":
                if "event" in name.lower():
                    performance["event_processing"]["avg_ms"] = metric["stats"].get("avg", 0)
                    performance["event_processing"]["p95_ms"] = metric["stats"].get("p95", 0)
                elif "api" in name.lower():
                    performance["api_latency"]["avg_ms"] = metric["stats"].get("avg", 0)
                    performance["api_latency"]["p95_ms"] = metric["stats"].get("p95", 0)
        
        return performance
    
    def _get_uptime(self) -> float:
        """Get system uptime (simplified)"""
        # In production, track actual start time
        return 3600.0  # Placeholder
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        return {
            "health": self.get_system_health(),
            "metrics": self.get_metrics_summary(),
            "performance": self.get_performance_metrics(),
            "timestamp": datetime.now().isoformat()
        }


# Global dashboard instance
dashboard = MetricsDashboard()


def get_dashboard_data() -> Dict[str, Any]:
    """Get dashboard data for API endpoint"""
    return dashboard.get_dashboard_data()
'''
    
    file_path = TELEMETRY_DIR / "dashboard.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_alerts():
    """Create alerts.py for alerting rules"""
    print("\n[5/6] Creating alerts...")
    
    content = '''"""
Alerts - Alerting Rules and Management
"""

from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """Alert instance"""
    name: str
    severity: AlertSeverity
    message: str
    status: AlertStatus = AlertStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)


class AlertManager:
    """Manage alerting rules and notifications - Singleton"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._rules: List[Dict[str, Any]] = []
        self._alerts: List[Alert] = []
        self._alert_history: List[Alert] = []
        self._notifiers: List[Callable] = []
        self._initialized = True
    
    def add_rule(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        severity: AlertSeverity,
        message: str,
        interval_seconds: int = 60
    ):
        """Add alerting rule"""
        self._rules.append({
            "name": name,
            "condition": condition,
            "severity": severity,
            "message": message,
            "interval": interval_seconds,
            "last_check": datetime.now()
        })
    
    def add_notifier(self, notifier: Callable[[Alert], None]):
        """Add notification handler"""
        self._notifiers.append(notifier)
    
    def check_rules(self, metrics: Dict[str, Any]):
        """Check all alerting rules against current metrics"""
        now = datetime.now()
        
        for rule in self._rules:
            # Check if enough time has passed
            last_check = rule.get("last_check")
            if last_check and (now - last_check).total_seconds() < rule["interval"]:
                continue
            
            rule["last_check"] = now
            condition = rule["condition"]
            
            try:
                if condition(metrics):
                    self._fire_alert(
                        name=rule["name"],
                        severity=rule["severity"],
                        message=rule["message"]
                    )
            except Exception as e:
                self._fire_alert(
                    name=f"alert_check_failed_{rule['name']}",
                    severity=AlertSeverity.ERROR,
                    message=f"Alert rule check failed: {e}"
                )
    
    def _fire_alert(self, name: str, severity: AlertSeverity, message: str):
        """Fire an alert"""
        # Check if alert already exists and is still firing
        existing = self._get_active_alert(name)
        if existing:
            existing.status = AlertStatus.FIRING
            existing.message = message
            return
        
        alert = Alert(
            name=name,
            severity=severity,
            message=message,
            status=AlertStatus.FIRING
        )
        self._alerts.append(alert)
        self._notify(alert)
    
    def _get_active_alert(self, name: str) -> Optional[Alert]:
        """Get active alert by name"""
        for alert in self._alerts:
            if alert.name == name and alert.status in [AlertStatus.PENDING, AlertStatus.FIRING]:
                return alert
        return None
    
    def resolve_alert(self, name: str):
        """Resolve an alert"""
        alert = self._get_active_alert(name)
        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            self._alert_history.append(alert)
            self._alerts.remove(alert)
            self._notify_resolved(alert)
    
    def _notify(self, alert: Alert):
        """Send notification for alert"""
        for notifier in self._notifiers:
            try:
                notifier(alert)
            except Exception as e:
                print(f"Notifier failed: {e}")
    
    def _notify_resolved(self, alert: Alert):
        """Send resolution notification"""
        # Similar to _notify but with resolved status
        for notifier in self._notifiers:
            try:
                notifier(alert)
            except Exception:
                pass
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently firing alerts"""
        return [
            {
                "name": a.name,
                "severity": a.severity.value,
                "message": a.message,
                "created_at": a.created_at.isoformat(),
                "status": a.status.value
            }
            for a in self._alerts
            if a.status in [AlertStatus.PENDING, AlertStatus.FIRING]
        ]
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history"""
        return [
            {
                "name": a.name,
                "severity": a.severity.value,
                "message": a.message,
                "created_at": a.created_at.isoformat(),
                "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
                "status": a.status.value
            }
            for a in self._alert_history[-limit:]
        ]


# Default alert rules
def setup_default_alerts(alert_manager: AlertManager):
    """Setup default alerting rules"""
    
    # High error rate alert
    def high_error_rate(metrics):
        error_count = metrics.get("counters", {}).get("errors_total", 0)
        request_count = metrics.get("counters", {}).get("requests_total", 1)
        return error_count / request_count > 0.05
    
    alert_manager.add_rule(
        name="high_error_rate",
        condition=high_error_rate,
        severity=AlertSeverity.CRITICAL,
        message="Error rate exceeds 5% threshold",
        interval_seconds=60
    )
    
    # Slow response alert
    def slow_response(metrics):
        avg_latency = metrics.get("histograms", {}).get("api_latency_ms", {}).get("avg", 0)
        return avg_latency > 500
    
    alert_manager.add_rule(
        name="slow_response",
        condition=slow_response,
        severity=AlertSeverity.WARNING,
        message="API response time exceeds 500ms",
        interval_seconds=120
    )
    
    # Memory high alert
    def high_memory(metrics):
        memory_usage = metrics.get("gauges", {}).get("memory_usage_mb", 0)
        return memory_usage > 1024  # 1GB
    
    alert_manager.add_rule(
        name="high_memory",
        condition=high_memory,
        severity=AlertSeverity.WARNING,
        message="Memory usage exceeds 1GB",
        interval_seconds=60
    )


# Global alert manager
alert_manager = AlertManager()
'''
    
    file_path = TELEMETRY_DIR / "alerts.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def enhance_health():
    """Enhance health.py with detailed checks"""
    print("\n[6/6] Enhancing health checks...")
    
    content = '''"""
Health - Health Check Endpoints
"""

from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
import asyncio


class HealthChecker:
    """Health check manager"""
    
    def __init__(self):
        self._checks: Dict[str, Callable] = {}
        self._results: Dict[str, Any] = {}
    
    def register(self, name: str, check_func: Callable, timeout: float = 5.0):
        """Register a health check"""
        self._checks[name] = {"func": check_func, "timeout": timeout}
    
    async def run_check(self, name: str) -> Dict[str, Any]:
        """Run a single health check"""
        check = self._checks.get(name)
        if not check:
            return {"status": "unknown", "error": f"Check '{name}' not found"}
        
        try:
            result = await asyncio.wait_for(check["func"](), timeout=check["timeout"])
            return {"status": "healthy", "details": result}
        except asyncio.TimeoutError:
            return {"status": "unhealthy", "error": f"Timeout after {check['timeout']}s"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def run_all(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall = "healthy"
        
        for name in self._checks:
            result = await self.run_check(name)
            results[name] = result
            if result["status"] != "healthy":
                overall = "unhealthy"
        
        return {
            "status": overall,
            "timestamp": datetime.now().isoformat(),
            "checks": results
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get cached health status"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }


# Global health checker
health_checker = HealthChecker()


# Default health checks
async def check_database():
    """Check database connectivity"""
    try:
        from backend.infrastructure.database import get_db
        db = get_db()
        await db.execute("SELECT 1")
        return {"database": "connected"}
    except Exception as e:
        raise Exception(f"Database connection failed: {e}")


async def check_event_bus():
    """Check event bus health"""
    try:
        from backend.core.events import EventBus
        bus = EventBus()
        metrics = bus.get_metrics()
        return {"event_bus": "healthy", "metrics": metrics}
    except Exception as e:
        raise Exception(f"Event bus unhealthy: {e}")


async def check_websocket():
    """Check WebSocket health"""
    try:
        from backend.websocket import ConnectionManager
        manager = ConnectionManager()
        return {"websocket": "healthy", "connections": manager.connection_count}
    except Exception as e:
        raise Exception(f"WebSocket unhealthy: {e}")


async def check_evidence():
    """Check evidence service health"""
    try:
        from backend.evidence import EvidenceRegistry
        registry = EvidenceRegistry()
        count = len(registry.list_all())
        return {"evidence": "healthy", "evidence_count": count}
    except Exception as e:
        raise Exception(f"Evidence service unhealthy: {e}")


# Register default health checks
health_checker.register("database", check_database)
health_checker.register("event_bus", check_event_bus)
health_checker.register("websocket", check_websocket)
health_checker.register("evidence", check_evidence)


async def get_health() -> Dict[str, Any]:
    """Get health status for API endpoint"""
    return await health_checker.run_all()


async def get_readiness() -> Dict[str, Any]:
    """Get readiness status for k8s probe"""
    result = await health_checker.run_all()
    return result


async def get_liveness() -> Dict[str, Any]:
    """Get liveness status for k8s probe"""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}
'''
    
    file_path = TELEMETRY_DIR / "health.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_telemetry_init():
    """Create __init__.py for telemetry"""
    print("\n[7/7] Creating telemetry __init__.py...")
    
    content = '''"""
NEMESIS Telemetry - Observability and Monitoring
"""

from backend.telemetry.metrics import (
    MetricsRegistry, metrics_registry, counter_inc, gauge_set,
    histogram_observe, timed_metric, Timer
)
from backend.telemetry.logging import get_logger, StructuredLogger, set_trace_context
from backend.telemetry.tracing import tracer, trace, Tracer
from backend.telemetry.dashboard import get_dashboard_data, MetricsDashboard
from backend.telemetry.alerts import alert_manager, AlertManager, AlertSeverity
from backend.telemetry.health import health_checker, get_health, get_readiness, get_liveness

__all__ = [
    'MetricsRegistry', 'metrics_registry', 'counter_inc', 'gauge_set',
    'histogram_observe', 'timed_metric', 'Timer',
    'get_logger', 'StructuredLogger', 'set_trace_context',
    'tracer', 'trace', 'Tracer',
    'get_dashboard_data', 'MetricsDashboard',
    'alert_manager', 'AlertManager', 'AlertSeverity',
    'health_checker', 'get_health', 'get_readiness', 'get_liveness'
]
'''
    
    file_path = TELEMETRY_DIR / "__init__.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def main():
    print("\n" + "="*60)
    print("FASE 5: CREATE TELEMETRY CORE")
    print("="*60)
    
    create_enhanced_metrics()
    create_enhanced_logging()
    create_tracing()
    create_dashboard()
    create_alerts()
    enhance_health()
    create_telemetry_init()
    
    print("\n" + "="*60)
    print("[OK] Telemetry core created")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())