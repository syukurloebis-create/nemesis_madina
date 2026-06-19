from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response, Request

# Metrics definitions
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
http_requests_in_progress = Gauge('http_requests_in_progress', 'Requests in progress', ['method'])

cases_created_total = Counter('cases_created_total', 'Total cases created', ['priority'])
collusion_detections_total = Counter('collusion_detections_total', 'Total collusion detections', ['pattern_type'])
service_up = Gauge('service_up', 'Service health status')


async def metrics_endpoint(request: Request = None):
    """Prometheus metrics endpoint"""
    service_up.set(1)
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ============================================
# Compatibility Shim (untuk kode lama)
# ============================================

class MetricsRegistry:
    pass


metrics_registry = MetricsRegistry()


def counter_inc(metric, value=1, **labels):
    if hasattr(metric, 'labels'):
        metric.labels(**labels).inc(value)
    else:
        metric.inc(value)


def gauge_set(metric, value, **labels):
    if hasattr(metric, 'labels'):
        metric.labels(**labels).set(value)
    else:
        metric.set(value)


def histogram_observe(metric, value, **labels):
    if hasattr(metric, 'labels'):
        metric.labels(**labels).observe(value)
    else:
        metric.observe(value)


def timed_metric(metric):
    def decorator(func):
        return func
    return decorator


class Timer:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
