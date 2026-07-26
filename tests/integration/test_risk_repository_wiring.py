"""
Integration Test - Risk Repository Wiring.

Verifies that RiskCollector receives the correct READ repository.
"""

import pytest
from backend.collectors.risk_collector import RiskCollector
from backend.repositories.sqlalchemy.risk_repository_impl import RiskRepositoryImpl


@pytest.mark.asyncio
async def test_risk_collector_uses_read_repository(container):
    """
    Test that RiskCollector receives RiskRepositoryImpl.
    
    This prevents regression where risk() might return the WRITE repository.
    """
    registry = container.collectors.registry
    
    risk_collector = registry.get("risk")
    
    assert risk_collector is not None
    assert isinstance(risk_collector, RiskCollector)
    
    # Access internal repository (white-box test)
    # This is acceptable for architecture regression testing
    repository = risk_collector._repository
    
    # Should be READ repository, not WRITE repository
    assert repository.__class__.__name__ == "RiskRepositoryImpl"
    
    # Should NOT be RiskCommandRepositoryImpl
    assert repository.__class__.__name__ != "RiskCommandRepositoryImpl"