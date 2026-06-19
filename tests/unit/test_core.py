"""
Unit tests for Core modules
"""

import pytest
from backend.core.entities.models import BaseEntity, EntityStatus, AnalysisResult, AnomalyReport
from backend.core.services.analysis import AnalysisService
from backend.core.services.anomaly import AnomalyService


class TestCoreEntities:
    """Test core entities"""
    
    def test_base_entity(self):
        entity = BaseEntity(id="test_001")
        assert entity.id == "test_001"
        assert entity.status == EntityStatus.ACTIVE
        assert entity.created_at is not None
    
    def test_analysis_result(self):
        result = AnalysisResult(
            id="res_001",
            entity_id="entity_001",
            analysis_type="risk",
            score=0.85,
            confidence=0.9
        )
        assert result.id == "res_001"
        assert result.entity_id == "entity_001"
        assert result.score == 0.85
        assert result.confidence == 0.9
    
    def test_anomaly_report(self):
        report = AnomalyReport(
            id="rep_001",
            source="detector",
            severity="high",
            description="Test anomaly"
        )
        assert report.id == "rep_001"
        assert report.source == "detector"
        assert report.severity == "high"
        assert report.resolved is False


class TestCoreServices:
    """Test core services"""
    
    def test_analysis_service(self):
        service = AnalysisService()
        result = service.record_result(
            entity_id="test",
            analysis_type="risk",
            score=0.75,
            confidence=0.8
        )
        assert result is not None
        assert result.score == 0.75
        
        results = service.get_results_for_entity("test")
        assert len(results) == 1
    
    def test_anomaly_service(self):
        service = AnomalyService()
        report = service.create_report(
            source="test",
            severity="medium",
            description="Test report"
        )
        assert report is not None
        assert report.severity == "medium"
        
        active = service.get_active_reports()
        assert len(active) == 1
