# tests/unit/test_core.py
"""
Core module tests - LEGACY
These tests are for the old backend.core.entities API which has been deprecated.
"""

import pytest

# ✅ Skip SEBELUM import - prevents collection error
pytest.skip(
    "Legacy backend.core.entities removed. "
    "These tests will be migrated to use domain layer entities.",
    allow_module_level=True,
)

# ============================================================
# IMPORTS (will not be executed due to skip above)
# ============================================================

from backend.core.entities.models import (
    BaseEntity,
    EntityStatus,
    AnalysisResult,
    AnomalyReport,
)


# ============================================================
# TESTS (will not be executed)
# ============================================================

class TestCoreEntities:
    """Legacy core entities tests - to be migrated."""

    def test_base_entity(self):
        """Test BaseEntity creation."""
        entity = BaseEntity(id="test-001", status=EntityStatus.ACTIVE)
        assert entity.id == "test-001"
        assert entity.status == EntityStatus.ACTIVE

    def test_entity_status(self):
        """Test EntityStatus enum."""
        assert EntityStatus.ACTIVE == "active"
        assert EntityStatus.INACTIVE == "inactive"
        assert EntityStatus.DELETED == "deleted"

    def test_analysis_result(self):
        """Test AnalysisResult creation."""
        result = AnalysisResult(
            finding_id="finding-001",
            score=0.85,
            confidence=0.92,
            status="completed"
        )
        assert result.finding_id == "finding-001"
        assert result.score == 0.85
        assert result.confidence == 0.92

    def test_anomaly_report(self):
        """Test AnomalyReport creation."""
        report = AnomalyReport(
            id="report-001",
            anomaly_type="fraud",
            severity="high",
            description="Suspicious transaction pattern detected"
        )
        assert report.id == "report-001"
        assert report.anomaly_type == "fraud"
        assert report.severity == "high"