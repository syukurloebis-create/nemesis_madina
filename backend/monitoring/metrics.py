from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from fastapi import APIRouter, Response
import time
from typing import Callable
import functools
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["monitoring"])

# ============================================
# HAPUS REGISTRY YANG SUDAH ADA (untuk development)
# ============================================

# Bersihkan collector yang sudah ada untuk menghindari duplicate
try:
    REGISTRY._names_to_collectors.clear()
except Exception:
    pass

# ============================================
# BASE METRICS
# ============================================

# Gunakan nama yang unik dengan prefix 'nemesis_'
http_requests_total = Counter(
    'nemesis_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

http_request_duration = Histogram(
    'nemesis_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
    registry=REGISTRY
)

active_requests = Gauge(
    'nemesis_http_active_requests',
    'Active HTTP requests',
    registry=REGISTRY
)

# ============================================
# BUSINESS METRICS (Nemesis Specific)
# ============================================

# Raw Data Metrics
nemesis_ingested_packages = Counter(
    'nemesis_ingested_packages_total',
    'Total packages ingested',
    ['source'],
    registry=REGISTRY
)

nemesis_normalized_packages = Counter(
    'nemesis_normalized_packages_total',
    'Total packages normalized',
    ['status'],
    registry=REGISTRY
)

# Entity Graph Metrics
nemesis_entity_nodes = Gauge(
    'nemesis_entity_nodes_total',
    'Total nodes in entity graph',
    ['node_type'],
    registry=REGISTRY
)

nemesis_entity_edges = Gauge(
    'nemesis_entity_edges_total',
    'Total edges in entity graph',
    ['edge_type'],
    registry=REGISTRY
)

# Risk Metrics
nemesis_risk_score = Gauge(
    'nemesis_risk_score',
    'Risk score for package',
    ['package_id', 'agency', 'category'],
    registry=REGISTRY
)

nemesis_anomaly_score = Gauge(
    'nemesis_anomaly_score',
    'Anomaly score for package',
    ['package_id'],
    registry=REGISTRY
)

nemesis_anomaly_detected = Counter(
    'nemesis_anomaly_detected_total',
    'Total anomalies detected',
    ['severity', 'type'],
    registry=REGISTRY
)

# Classification Metrics
nemesis_classification_count = Gauge(
    'nemesis_classification_count',
    'Number of packages by classification',
    ['classification'],
    registry=REGISTRY
)

# Budget Metrics
nemesis_budget_total = Gauge(
    'nemesis_budget_total',
    'Total budget by sector and year',
    ['sector', 'year'],
    registry=REGISTRY
)

nemesis_budget_trend = Gauge(
    'nemesis_budget_trend',
    'Budget trend over time',
    ['sector', 'month'],
    registry=REGISTRY
)

# Audit & Integrity Metrics
nemesis_hash_verification_failures = Counter(
    'nemesis_hash_verification_failures_total',
    'Total hash chain verification failures',
    ['case_id'],
    registry=REGISTRY
)

nemesis_evidence_hashes = Gauge(
    'nemesis_evidence_hashes_total',
    'Total evidence files with valid hashes',
    registry=REGISTRY
)

nemesis_evidence_integrity_failures = Counter(
    'nemesis_evidence_integrity_failures_total',
    'Evidence integrity check failures',
    ['evidence_id'],
    registry=REGISTRY
)

nemesis_compliance_score = Gauge(
    'nemesis_compliance_score',
    'Overall compliance score',
    ['institution'],
    registry=REGISTRY
)

# AI Intelligence Metrics
nemesis_ai_explanations = Counter(
    'nemesis_ai_explanations_total',
    'Total AI explanations generated',
    ['reason_code'],
    registry=REGISTRY
)

nemesis_red_flags = Gauge(
    'nemesis_red_flags_total',
    'Total red flags detected',
    ['institution', 'severity'],
    registry=REGISTRY
)

# Benchmark Metrics
nemesis_benchmark_ratio = Gauge(
    'nemesis_benchmark_ratio',
    'Price vs benchmark ratio',
    ['package_id', 'sector'],
    registry=REGISTRY
)

nemesis_deviation_index = Gauge(
    'nemesis_deviation_index',
    'Deviation from standard',
    ['sector', 'agency'],
    registry=REGISTRY
)

# Lineage Metrics
nemesis_lineage_depth = Gauge(
    'nemesis_lineage_depth',
    'Data lineage depth',
    ['package_id'],
    registry=REGISTRY
)

# Relationship Metrics
nemesis_relationship_strength = Gauge(
    'nemesis_relationship_strength',
    'Strength of entity relationship',
    ['source', 'target', 'relationship_type'],
    registry=REGISTRY
)


def track_metrics(endpoint: str):
    """Decorator to track request metrics"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            active_requests.inc()
            start_time = time.time()
            try:
                response = await func(*args, **kwargs)
                status_code = response.status_code if hasattr(response, 'status_code') else 200
                http_requests_total.labels(method='GET', endpoint=endpoint, status=status_code).inc()
                return response
            except Exception as e:
                http_requests_total.labels(method='GET', endpoint=endpoint, status=500).inc()
                raise
            finally:
                duration = time.time() - start_time
                http_request_duration.labels(method='GET', endpoint=endpoint).observe(duration)
                active_requests.dec()
        return wrapper
    return decorator


@router.get("")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/health")
async def metrics_health():
    """Health check for metrics endpoint"""
    return {"status": "healthy", "metrics_count": len(REGISTRY._names_to_collectors)}