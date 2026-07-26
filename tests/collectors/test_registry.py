"""
Collector Registry Test.
"""

import pytest

from backend.collectors.registry import CollectorRegistry
from backend.collectors.interfaces.collector import ICollector
from backend.collectors.exceptions import CollectorNotFoundError


class MockCollector(ICollector):
    """Mock collector untuk testing registry."""
    async def collect(self, uow, context):
        return None


class TestCollectorRegistry:
    """Collector Registry Tests."""

    def test_registry_returns_correct_collector(self):
        """Test registry.get returns correct collector."""
        registry = CollectorRegistry({
            "fraud": MockCollector(),
            "risk": MockCollector(),
        })

        fraud = registry.get("fraud")
        risk = registry.get("risk")

        assert fraud is not None
        assert risk is not None
        assert registry.get("fraud") is fraud

    def test_registry_get_all_returns_all(self):
        """Test registry.get_all returns all collectors."""
        registry = CollectorRegistry({
            "fraud": MockCollector(),
            "risk": MockCollector(),
        })

        all_collectors = registry.get_all()

        assert len(all_collectors) == 2

    def test_registry_raises_collector_not_found_error(self):
        """Test registry raises CollectorNotFoundError for unknown collector."""
        registry = CollectorRegistry({})

        with pytest.raises(CollectorNotFoundError) as exc:
            registry.get("unknown")

        assert exc.value.name == "unknown"
        assert "unknown" in str(exc.value)