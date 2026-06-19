#!/usr/bin/env python3
"""
NEMESIS FASE 6 - Create pytest configuration
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def create_conftest():
    """Create conftest.py with fixtures"""
    print("\n[1/5] Creating conftest.py...")
    
    content = '''"""
Pytest Configuration and Fixtures
"""

import pytest
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, AsyncGenerator

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
async def evidence_registry():
    """Create evidence registry for testing"""
    from backend.evidence import EvidenceRegistry
    registry = EvidenceRegistry()
    # Clear before test
    registry.clear()
    yield registry
    registry.clear()


@pytest.fixture
async def event_bus():
    """Create event bus for testing"""
    from backend.core.events import EventBus
    bus = EventBus()
    bus.clear_history()
    yield bus
    bus.clear_history()


@pytest.fixture
async def lineage_tracker():
    """Create lineage tracker for testing"""
    from backend.lineage import LineageTracker
    tracker = LineageTracker()
    tracker.clear()
    yield tracker
    tracker.clear()


@pytest.fixture
def sample_evidence_data() -> Dict[str, Any]:
    """Sample evidence data for testing"""
    return {
        "id": "test_evidence_001",
        "payload": {
            "event_type": "test",
            "data": {"key": "value"},
            "timestamp": "2024-01-01T00:00:00"
        },
        "source": "unit_test",
        "metadata": {"test": True}
    }


@pytest.fixture
def sample_event_data() -> Dict[str, Any]:
    """Sample event data for testing"""
    return {
        "event_type": "test.event",
        "data": {"test_id": 123, "message": "hello"},
        "source": "unit_test"
    }


@pytest.fixture
def sample_graph_data() -> Dict[str, Any]:
    """Sample graph data for testing"""
    return {
        "nodes": [
            {"id": "A", "label": "Node A"},
            {"id": "B", "label": "Node B"},
            {"id": "C", "label": "Node C"}
        ],
        "edges": [
            {"source": "A", "target": "B", "label": "connected"},
            {"source": "B", "target": "C", "label": "connected"}
        ]
    }


@pytest.fixture
def mock_metrics_registry():
    """Mock metrics registry for testing"""
    from backend.telemetry.metrics import MetricsRegistry
    registry = MetricsRegistry()
    registry.reset()
    yield registry
    registry.reset()


# Async fixture helper
@pytest.fixture
def anyio_backend():
    """Set anyio backend for async tests"""
    return "asyncio"
'''
    
    file_path = PROJECT_ROOT / "tests" / "conftest.py"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_pytest_ini():
    """Create pytest.ini configuration"""
    print("\n[2/5] Creating pytest.ini...")
    
    content = '''[pytest]
# Pytest configuration for NEMESIS

# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Asyncio mode
asyncio_mode = auto

# Add options
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=backend
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=70

# Markers
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow running tests
    async: Async tests

# Logging
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)s] %(message)s
log_cli_date_format = %H:%M:%S

# Filter warnings
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning

# Timeout
timeout = 300
timeout_method = thread
'''
    
    file_path = PROJECT_ROOT / "pytest.ini"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_unit_tests():
    """Create unit test files"""
    print("\n[3/5] Creating unit tests...")
    
    # Create unit test directory
    unit_dir = PROJECT_ROOT / "tests" / "unit"
    unit_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py
    (unit_dir / "__init__.py").write_text('"""Unit tests for NEMESIS"""')
    
    # Test evidence
    evidence_test = '''"""
Unit tests for Evidence module
"""

import pytest
from backend.evidence import EvidenceRegistry, EvidenceHasher
from backend.evidence.dto import Evidence, CustodyEvent, EvidenceType


class TestEvidenceHasher:
    """Test evidence hashing"""
    
    def test_compute_hash_deterministic(self):
        hasher = EvidenceHasher()
        data = {"test": "data", "number": 123}
        
        hash1 = hasher.compute_hash(data)
        hash2 = hasher.compute_hash(data)
        
        assert hash1 == hash2
        assert len(hash1) == 64
    
    def test_compute_hash_different_data(self):
        hasher = EvidenceHasher()
        hash1 = hasher.compute_hash({"a": 1})
        hash2 = hasher.compute_hash({"a": 2})
        
        assert hash1 != hash2
    
    def test_compute_hash_empty_data(self):
        hasher = EvidenceHasher()
        hash_val = hasher.compute_hash({})
        assert len(hash_val) == 64
    
    def test_compute_chain_hash(self):
        hasher = EvidenceHasher()
        hashes = ["hash1", "hash2", "hash3"]
        chain_hash = hasher.compute_chain_hash(hashes)
        assert len(chain_hash) == 64


class TestEvidenceRegistry:
    """Test evidence registry"""
    
    def test_create_evidence(self, evidence_registry):
        evidence = evidence_registry.create(
            payload={"test": "data"},
            source="test"
        )
        
        assert evidence.id is not None
        assert evidence.hash is not None
        assert evidence.source == "test"
        assert len(evidence.custody_chain) == 1
    
    def test_get_evidence(self, evidence_registry):
        created = evidence_registry.create({"test": "data"}, "test")
        retrieved = evidence_registry.get(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.hash == created.hash
    
    def test_verify_evidence(self, evidence_registry):
        evidence = evidence_registry.create({"test": "data"}, "test")
        is_valid = evidence_registry.verify(evidence.id)
        
        assert is_valid is True
    
    def test_verify_tampered_evidence(self, evidence_registry):
        evidence = evidence_registry.create({"test": "data"}, "test")
        # Tamper with evidence
        evidence.payload["test"] = "tampered"
        
        is_valid = evidence_registry.verify(evidence.id)
        assert is_valid is False
    
    def test_add_custody_event(self, evidence_registry):
        evidence = evidence_registry.create({"test": "data"}, "test")
        updated = evidence_registry.add_custody_event(
            evidence.id,
            action="verified",
            actor="verifier",
            reason="Integrity check passed"
        )
        
        assert updated is not None
        assert len(updated.custody_chain) == 2
        assert updated.custody_chain[-1].action == "verified"
        assert updated.version == 2
    
    def test_list_evidence(self, evidence_registry):
        evidence_registry.create({"test": "data1"}, "test")
        evidence_registry.create({"test": "data2"}, "test")
        evidence_registry.create({"test": "data3"}, "test")
        
        all_evidence = evidence_registry.list_all()
        assert len(all_evidence) == 3


class TestChainValidator:
    """Test chain validator"""
    
    def test_validate_chain(self, evidence_registry):
        from backend.evidence.chain_validator import ChainValidator
        validator = ChainValidator()
        
        # Create chain
        v1 = evidence_registry.create({"data": "v1"}, "test")
        v2 = evidence_registry.create({"data": "v2"}, "test")
        
        chain = [
            {"index": 0, "previous_hash": "0", "timestamp": v1.created_at.isoformat(), "data_hash": v1.hash, "hash": v1.hash},
            {"index": 1, "previous_hash": v1.hash, "timestamp": v2.created_at.isoformat(), "data_hash": v2.hash, "hash": v2.hash}
        ]
        
        valid, errors = validator.validate_chain(chain)
        assert valid is True
        assert len(errors) == 0
'''
    (unit_dir / "test_evidence.py").write_text(evidence_test)
    print("  [OK] Created test_evidence.py")
    
    # Test intelligence
    intelligence_test = '''"""
Unit tests for Intelligence module
"""

import pytest
from backend.intelligence.ml import AnomalyDetector, RiskScorer, ConfidenceCalibrator
from backend.intelligence.legal import AuditTrailValidator, ComplianceChecker
from backend.intelligence.explainability import ModelExplainer


class TestAnomalyDetector:
    """Test anomaly detection"""
    
    def test_detect_zscore_anomalies(self):
        detector = AnomalyDetector(method="zscore", threshold=3.0)
        data = [1, 2, 3, 100, 4, 5, 6]
        
        anomalies = detector.detect(data)
        assert anomalies == [3]
    
    def test_detect_iqr_anomalies(self):
        detector = AnomalyDetector(method="iqr")
        data = [1, 2, 3, 100, 4, 5, 6]
        
        anomalies = detector.detect(data)
        assert 3 in anomalies
    
    def test_detect_no_anomalies(self):
        detector = AnomalyDetector()
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        anomalies = detector.detect(data)
        assert len(anomalies) == 0
    
    def test_online_detection(self):
        detector = AnomalyDetector()
        # Warm up with normal data
        for i in range(50):
            detector._history.append(i)
        
        is_anomaly, score = detector.detect_online(100)
        assert is_anomaly is True
        assert score > 0
    
    def test_get_anomaly_score(self):
        detector = AnomalyDetector()
        historical = [1, 2, 3, 4, 5]
        
        score_normal = detector.get_anomaly_score(3, historical)
        score_anomaly = detector.get_anomaly_score(100, historical)
        
        assert score_normal < score_anomaly


class TestRiskScorer:
    """Test risk scoring"""
    
    def test_compute_score(self):
        scorer = RiskScorer()
        features = {
            "anomaly_score": 0.8,
            "collusion_risk": 0.6,
            "historical_risk": 0.4
        }
        
        score = scorer.compute_score(features)
        assert 0 <= score <= 1
    
    def test_get_severity(self):
        scorer = RiskScorer()
        
        assert scorer.get_severity(0.9) == "critical"
        assert scorer.get_severity(0.7) == "high"
        assert scorer.get_severity(0.5) == "medium"
        assert scorer.get_severity(0.3) == "low"
        assert scorer.get_severity(0.1) == "info"
    
    def test_empty_features(self):
        scorer = RiskScorer()
        score = scorer.compute_score({})
        assert 0 <= score <= 1
    
    def test_dynamic_weights(self):
        scorer = RiskScorer()
        scorer.enable_dynamic_weights(True)
        
        features = {"anomaly_score": 0.9}
        score = scorer.compute_dynamic_score(features, {"time_of_day": "night"})
        assert score > 0


class TestConfidenceCalibrator:
    """Test confidence calibration"""
    
    def test_calibrate_insufficient_data(self):
        calibrator = ConfidenceCalibrator()
        raw_score = 0.8
        
        calibrated = calibrator.calibrate(raw_score)
        assert calibrated == raw_score
    
    def test_add_calibration_point(self):
        calibrator = ConfidenceCalibrator()
        calibrator.add_calibration_point(0.8, True)
        calibrator.add_calibration_point(0.6, False)
        
        assert len(calibrator.calibration_data) == 2
    
    def test_calibration_metrics(self):
        calibrator = ConfidenceCalibrator()
        for i in range(50):
            calibrator.add_calibration_point(0.7 + i * 0.01, i % 2 == 0)
        
        metrics = calibrator.get_calibration_metrics()
        assert "brier_score" in metrics
        assert "ece" in metrics


class TestModelExplainer:
    """Test model explainability"""
    
    def test_explain_prediction(self):
        explainer = ModelExplainer()
        features = {"feature1": 0.8, "feature2": 0.3, "feature3": 0.5}
        
        explanation = explainer.explain("pred_123", features, 0.75)
        
        assert explanation["prediction_id"] == "pred_123"
        assert explanation["prediction"] == 0.75
        assert "top_features" in explanation
        assert len(explanation["top_features"]) <= 5
    
    def test_get_explanation(self):
        explainer = ModelExplainer()
        explainer.explain("pred_123", {"f1": 0.8}, 0.75)
        
        retrieved = explainer.get("pred_123")
        assert retrieved is not None
        assert retrieved["prediction_id"] == "pred_123"
    
    def test_counterfactual(self):
        explainer = ModelExplainer()
        
        def mock_predict(features):
            return features.get("score", 0.5)
        
        instance = {"score": 0.3}
        result = explainer.explain_counterfactual(
            instance, 0.8, mock_predict, ["score"], max_iterations=10
        )
        
        assert "changes" in result
'''
    (unit_dir / "test_intelligence.py").write_text(intelligence_test)
    print("  [OK] Created test_intelligence.py")
    
    # Test telemetry
    telemetry_test = '''"""
Unit tests for Telemetry module
"""

import pytest
from backend.telemetry.metrics import MetricsRegistry, counter_inc, gauge_set, histogram_observe


class TestMetricsRegistry:
    """Test metrics registry"""
    
    def test_counter_increment(self):
        registry = MetricsRegistry()
        registry.reset()
        
        registry.counter("test_counter", value=1)
        registry.counter("test_counter", value=2)
        
        assert registry.get_counter("test_counter") == 3
    
    def test_gauge_set(self):
        registry = MetricsRegistry()
        registry.gauge("test_gauge", 100)
        
        assert registry.get_gauge("test_gauge") == 100
        
        registry.gauge("test_gauge", 50)
        assert registry.get_gauge("test_gauge") == 50
    
    def test_histogram_observe(self):
        registry = MetricsRegistry()
        
        for i in range(100):
            registry.histogram("test_hist", float(i))
        
        stats = registry.get_histogram_stats("test_hist")
        assert stats["count"] == 100
        assert stats["min"] == 0
        assert stats["max"] == 99
        assert stats["avg"] == 49.5
    
    def test_get_all_metrics(self):
        registry = MetricsRegistry()
        registry.reset()
        
        registry.counter("counter1", 5)
        registry.gauge("gauge1", 42)
        
        metrics = registry.get_all_metrics()
        assert "counter1" in metrics
        assert "gauge1" in metrics
        assert metrics["counter1"]["value"] == 5
        assert metrics["gauge1"]["value"] == 42
    
    def test_prometheus_format(self):
        registry = MetricsRegistry()
        registry.reset()
        
        registry.counter("test_counter", 10)
        registry.gauge("test_gauge", 3.14)
        
        output = registry.get_prometheus_format()
        assert "test_counter 10" in output
        assert "test_gauge 3.14" in output


class TestConvenienceFunctions:
    """Test convenience metric functions"""
    
    def setup_method(self):
        from backend.telemetry.metrics import metrics_registry
        metrics_registry.reset()
    
    def test_counter_inc(self):
        counter_inc("test", 5)
        counter_inc("test", 3)
        
        from backend.telemetry.metrics import metrics_registry
        assert metrics_registry.get_counter("test") == 8
    
    def test_gauge_set(self):
        gauge_set("test", 100)
        
        from backend.telemetry.metrics import metrics_registry
        assert metrics_registry.get_gauge("test") == 100
    
    def test_histogram_observe(self):
        histogram_observe("test", 50)
        
        from backend.telemetry.metrics import metrics_registry
        stats = metrics_registry.get_histogram_stats("test")
        assert stats["count"] == 1
        assert stats["sum"] == 50


class TestTimerContext:
    """Test timer context manager"""
    
    def test_timer_records_duration(self):
        from backend.telemetry.metrics import Timer, metrics_registry
        import time
        
        metrics_registry.reset()
        
        with Timer("test_operation"):
            time.sleep(0.01)
        
        stats = metrics_registry.get_histogram_stats("test_operation")
        assert stats["count"] == 1
        assert stats["sum"] > 0
'''
    (unit_dir / "test_telemetry.py").write_text(telemetry_test)
    print("  [OK] Created test_telemetry.py")
    
    return True

def create_integration_tests():
    """Create integration test files"""
    print("\n[4/5] Creating integration tests...")
    
    # Create integration test directory
    int_dir = PROJECT_ROOT / "tests" / "integration"
    int_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py
    (int_dir / "__init__.py").write_text('"""Integration tests for NEMESIS"""')
    
    # Test event to projection
    event_projection_test = '''"""
Integration test: Event to Projection flow
"""

import pytest
import asyncio
from datetime import datetime


@pytest.mark.integration
@pytest.mark.asyncio
async def test_event_to_projection_flow(event_bus):
    """Test that events are properly projected"""
    received_events = []
    
    async def test_handler(event):
        received_events.append(event)
    
    event_bus.subscribe("test.event", test_handler)
    
    # Create test event
    from backend.core.events.bus import Event
    test_event = Event(
        id="test_001",
        type="test.event",
        data={"message": "hello"},
        source="integration_test",
        timestamp=datetime.now()
    )
    
    # Publish event
    await event_bus.publish(test_event)
    await asyncio.sleep(0.1)
    
    assert len(received_events) == 1
    assert received_events[0].id == "test_001"
    assert received_events[0].type == "test.event"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_subscribers(event_bus):
    """Test multiple subscribers to same event"""
    results = []
    
    async def handler1(event):
        results.append("handler1")
    
    async def handler2(event):
        results.append("handler2")
    
    event_bus.subscribe("test.event", handler1)
    event_bus.subscribe("test.event", handler2)
    
    from backend.core.events.bus import Event
    test_event = Event(
        id="test_002",
        type="test.event",
        data={},
        source="integration_test",
        timestamp=datetime.now()
    )
    
    await event_bus.publish(test_event)
    await asyncio.sleep(0.1)
    
    assert len(results) == 2
    assert "handler1" in results
    assert "handler2" in results


@pytest.mark.integration
@pytest.mark.asyncio
async def test_event_history(event_bus):
    """Test event history tracking"""
    from backend.core.events.bus import Event
    import uuid
    
    events = []
    for i in range(5):
        event = Event(
            id=str(uuid.uuid4()),
            type="test.event",
            data={"index": i},
            source="integration_test",
            timestamp=datetime.now()
        )
        await event_bus.publish(event)
        events.append(event)
    
    await asyncio.sleep(0.1)
    
    history = event_bus.get_history(limit=10)
    assert len(history) >= 5
    assert any(e.type == "test.event" for e in history)
'''
    (int_dir / "test_event_to_projection.py").write_text(event_projection_test)
    print("  [OK] Created test_event_to_projection.py")
    
    # Test evidence lineage
    evidence_lineage_test = '''"""
Integration test: Evidence and Lineage integration
"""

import pytest


@pytest.mark.integration
def test_evidence_lineage_integration(evidence_registry, lineage_tracker):
    """Test evidence and lineage integration"""
    # Create evidence
    evidence = evidence_registry.create(
        payload={"test": "integration_data"},
        source="integration_test"
    )
    
    # Track in lineage
    evidence_node = lineage_tracker.create_node(
        node_type="evidence",
        name=evidence.id,
        metadata={"hash": evidence.hash}
    )
    
    assert evidence_node is not None
    assert evidence_node.id is not None
    assert evidence_node.type == "evidence"
    assert evidence_node.metadata.get("hash") == evidence.hash
    
    # Add processing node
    process_node = lineage_tracker.create_node(
        node_type="transform",
        name="processing"
    )
    
    # Link nodes
    lineage_tracker.add_edge(evidence_node.id, process_node.id, "consumes")
    
    # Verify path
    path = lineage_tracker.get_path(evidence_node.id, process_node.id)
    assert path is not None
    assert len(path) == 2
    assert path[0] == evidence_node.id
    assert path[1] == process_node.id


@pytest.mark.integration
def test_lineage_impact_analysis(evidence_registry, lineage_tracker):
    """Test lineage impact analysis"""
    # Create multiple evidence
    ev1 = evidence_registry.create({"data": "ev1"}, "test")
    ev2 = evidence_registry.create({"data": "ev2"}, "test")
    ev3 = evidence_registry.create({"data": "ev3"}, "test")
    
    # Create nodes
    n1 = lineage_tracker.create_node("evidence", ev1.id)
    n2 = lineage_tracker.create_node("evidence", ev2.id)
    n3 = lineage_tracker.create_node("evidence", ev3.id)
    
    # Create processing node
    processor = lineage_tracker.create_node("transform", "processor")
    
    # Connect all to processor
    lineage_tracker.add_edge(n1.id, processor.id, "consumes")
    lineage_tracker.add_edge(n2.id, processor.id, "consumes")
    lineage_tracker.add_edge(n3.id, processor.id, "consumes")
    
    # Check impact
    impact = lineage_tracker.get_impact(n1.id)
    assert processor.id in [n.id for n in impact]
'''
    (int_dir / "test_evidence_lineage.py").write_text(evidence_lineage_test)
    print("  [OK] Created test_evidence_lineage.py")
    
    return True

def create_performance_tests():
    """Create performance test files"""
    print("\n[5/5] Creating performance tests...")
    
    # Create performance test directory
    perf_dir = PROJECT_ROOT / "tests" / "performance"
    perf_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py
    (perf_dir / "__init__.py").write_text('"""Performance tests for NEMESIS"""')
    
    # Load test
    load_test = '''"""
Performance: Load testing
"""

import pytest
import asyncio
import time
from datetime import datetime


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_event_throughput(event_bus):
    """Test event processing throughput"""
    from backend.core.events.bus import Event
    
    events_processed = 0
    
    async def handler(event):
        nonlocal events_processed
        events_processed += 1
    
    event_bus.subscribe("perf.event", handler)
    
    # Create events
    start_time = time.perf_counter()
    event_count = 100
    
    for i in range(event_count):
        event = Event(
            id=f"perf_{i}",
            type="perf.event",
            data={"index": i},
            source="perf_test",
            timestamp=datetime.now()
        )
        await event_bus.publish(event)
    
    # Give time for processing
    await asyncio.sleep(1)
    
    duration = time.perf_counter() - start_time
    throughput = events_processed / duration
    
    print(f"Processed {events_processed} events in {duration:.2f}s")
    print(f"Throughput: {throughput:.0f} events/sec")
    
    # Assert minimum performance
    assert events_processed >= event_count
    assert throughput > 50  # At least 50 events per second


@pytest.mark.performance
@pytest.mark.slow
def test_hash_computation_speed(evidence_registry):
    """Test hash computation performance"""
    from backend.evidence import EvidenceHasher
    import time
    
    hasher = EvidenceHasher()
    data = {"large": "data" * 1000}
    
    iterations = 1000
    start = time.perf_counter()
    
    for _ in range(iterations):
        hasher.compute_hash(data)
    
    duration = time.perf_counter() - start
    avg_ms = (duration / iterations) * 1000
    
    print(f"Average hash time: {avg_ms:.3f}ms")
    assert avg_ms < 5  # Should be under 5ms


@pytest.mark.performance
@pytest.mark.slow
def test_evidence_creation_speed(evidence_registry):
    """Test evidence creation performance"""
    import time
    
    iterations = 500
    start = time.perf_counter()
    
    for i in range(iterations):
        evidence_registry.create(
            payload={"test": i},
            source="perf_test"
        )
    
    duration = time.perf_counter() - start
    avg_ms = (duration / iterations) * 1000
    
    print(f"Average creation time: {avg_ms:.3f}ms")
    assert avg_ms < 10  # Should be under 10ms
'''
    (perf_dir / "test_load.py").write_text(load_test)
    print("  [OK] Created test_load.py")
    
    # Concurrency test
    concurrency_test = '''"""
Performance: Concurrency testing
"""

import pytest
import asyncio
from datetime import datetime


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_concurrent_event_publishing(event_bus):
    """Test concurrent event publishing"""
    from backend.core.events.bus import Event
    
    results = []
    
    async def handler(event):
        results.append(event.id)
        await asyncio.sleep(0)  # Yield control
    
    event_bus.subscribe("concurrent.event", handler)
    
    async def publish_events(start_id, count):
        for i in range(count):
            event = Event(
                id=f"concurrent_{start_id}_{i}",
                type="concurrent.event",
                data={"index": i},
                source="concurrent_test",
                timestamp=datetime.now()
            )
            await event_bus.publish(event)
    
    # Run concurrent publishers
    tasks = []
    for publisher_id in range(5):
        tasks.append(publish_events(publisher_id, 20))
    
    await asyncio.gather(*tasks)
    await asyncio.sleep(0.5)
    
    assert len(results) == 100  # 5 * 20 = 100 events
    print(f"Successfully processed {len(results)} concurrent events")


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_concurrent_evidence_creation(evidence_registry):
    """Test concurrent evidence creation"""
    import asyncio
    
    async def create_evidence(registry, evidence_id):
        return registry.create(
            payload={"id": evidence_id},
            source="concurrent_test"
        )
    
    # Create many evidences concurrently
    tasks = [create_evidence(evidence_registry, i) for i in range(100)]
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 100
    assert all(r.id is not None for r in results)
    print(f"Successfully created {len(results)} evidences concurrently")
'''
    (perf_dir / "test_concurrency.py").write_text(concurrency_test)
    print("  [OK] Created test_concurrency.py")
    
    return True

def main():
    print("\n" + "="*60)
    print("FASE 6: CREATE TESTING MATRIX")
    print("="*60)
    
    create_conftest()
    create_pytest_ini()
    create_unit_tests()
    create_integration_tests()
    create_performance_tests()
    
    print("\n" + "="*60)
    print("[OK] Testing matrix created")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())