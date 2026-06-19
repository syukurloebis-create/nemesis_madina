"""
Pytest Configuration and Fixtures
"""

import pytest
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

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
def evidence_registry():
    """Create evidence registry for testing"""
    from backend.evidence import EvidenceRegistry
    registry = EvidenceRegistry()
    # Clear before test
    registry.clear()
    yield registry
    registry.clear()


@pytest.fixture
def event_bus():
    """Create event bus for testing"""
    from backend.core.events import EventBus
    bus = EventBus()
    bus.clear_history()
    yield bus
    bus.clear_history()


@pytest.fixture
def lineage_tracker():
    """Create lineage tracker for testing"""
    from backend.lineage import LineageTracker
    tracker = LineageTracker()
    tracker.clear()
    yield tracker
    tracker.clear()


@pytest.fixture
def graph_builder():
    """Create graph builder for testing"""
    from backend.graph import GraphBuilder
    builder = GraphBuilder()
    yield builder
    builder.clear()


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
def anyio_backend():
    """Set anyio backend for async tests"""
    return "asyncio"
