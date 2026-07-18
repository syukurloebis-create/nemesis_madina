# backend/telemetry/metrics.py

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from typing import Dict, Any
import time

# Pipeline metrics
pipeline_execution_duration = Histogram(
    'nemesis_pipeline_duration_seconds',
    'Pipeline execution duration',
    ['pipeline_name', 'status'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

pipeline_execution_total = Counter(
    'nemesis_pipeline_executions_total',
    'Total pipeline executions',
    ['pipeline_name', 'status']
)

pipeline_execution_failures = Counter(
    'nemesis_pipeline_failures_total',
    'Total pipeline failures',
    ['pipeline_name', 'error_type']
)

# Orchestration metrics
orchestration_duration = Histogram(
    'nemesis_orchestration_duration_seconds',
    'Orchestration execution duration',
    ['status'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)


orchestration_total = Counter(
    'nemesis_orchestrations_total',
    'Total orchestrations executed',
    ['status']
)

# Circuit breaker metrics
circuit_breaker_state = Gauge(
    'nemesis_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half_open)',
    ['circuit_name']
)

circuit_breaker_failures = Counter(
    'nemesis_circuit_breaker_failures_total',
    'Total circuit breaker failures',
    ['circuit_name']
)

# Dashboard metrics
dashboard_response_duration = Histogram(
    'nemesis_dashboard_response_duration_seconds',
    'Dashboard response duration',
    ['status'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

dashboard_requests_total = Counter(
    'nemesis_dashboard_requests_total',
    'Total dashboard requests',
    ['status', 'endpoint']
)

# System metrics
active_pipelines = Gauge(
    'nemesis_active_pipelines',
    'Number of active pipelines'
)

pipeline_registry_size = Gauge(
    'nemesis_pipeline_registry_size',
    'Number of registered pipelines'
)

service_up = Gauge(
    "nemesis_service_up",
    "Service availability"
)


def record_pipeline_execution(name: str, duration_seconds: float, success: bool, error_type: str = None):
    """Record pipeline execution metrics."""
    status = "success" if success else "failure"
    pipeline_execution_duration.labels(pipeline_name=name, status=status).observe(duration_seconds)
    pipeline_execution_total.labels(pipeline_name=name, status=status).inc()
    
    if not success and error_type:
        pipeline_execution_failures.labels(pipeline_name=name, error_type=error_type).inc()


def record_orchestration(duration_seconds: float, success: bool):
    """Record orchestration metrics."""
    status = "success" if success else "failure"
    orchestration_duration.labels(status=status).observe(duration_seconds)
    orchestration_total.labels(status=status).inc()


def record_circuit_breaker_state(name: str, state: str):
    """Record circuit breaker state."""
    state_map = {"closed": 0, "open": 1, "half_open": 2}
    circuit_breaker_state.labels(circuit_name=name).set(state_map.get(state, 0))


def record_dashboard_request(duration_seconds: float, status_code: int, endpoint: str):
    """Record dashboard request metrics."""
    status = "success" if status_code < 400 else "error"
    dashboard_response_duration.labels(status=status).observe(duration_seconds)
    dashboard_requests_total.labels(status=status, endpoint=endpoint).inc()


def update_pipeline_registry_size(size: int):
    """Update pipeline registry size gauge."""
    pipeline_registry_size.set(size)

