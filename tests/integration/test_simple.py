"""
Simple integration tests that should always pass
"""

import pytest


@pytest.mark.integration
def test_import_evidence():
    """Test evidence module import"""
    from backend.evidence import EvidenceRegistry
    assert EvidenceRegistry is not None


@pytest.mark.integration
def test_import_graph():
    """Test graph module import"""
    from backend.graph import GraphBuilder
    assert GraphBuilder is not None


@pytest.mark.integration
def test_import_events():
    """Test events module import"""
    from backend.core.events import EventBus
    assert EventBus is not None
