"""
NEMESIS Madina - Aggregate Concurrency Tests
"""

import pytest
import asyncio
from uuid import uuid4

from backend.domain.aggregates.case_intelligence import CaseIntelligenceAggregate
from backend.domain.value_objects.case_id import CaseId
from backend.domain.value_objects.fraud_analysis import FraudAnalysis
from backend.domain.value_objects.fraud_pattern import FraudPattern
from backend.domain.enums.risk_level import RiskLevel


class TestAggregateConcurrency:
    def test_optimistic_locking_version_increment(self):
        """Version increments on every event."""
        aggregate = CaseIntelligenceAggregate(case_id=CaseId.generate())
        assert aggregate.version == 0
        
        analysis = FraudAnalysis(
            case_id=str(uuid4()),
            patterns=[],
            overall_risk=RiskLevel.LOW,
            score=10.0,
            total_patterns=0,
            active_alerts=0,
            high_confidence=0,
            validated_patterns=0,
            highest_confidence=0.0,
            average_confidence=0.0,
        )
        aggregate.record_analysis(analysis)
        assert aggregate.version == 1
    
    def test_rehydration_no_events(self):
        """Rehydration does NOT create events."""
        aggregate = CaseIntelligenceAggregate.rehydrate(
            case_id=CaseId.generate(),
            fraud=FraudAnalysis(
                case_id=str(uuid4()),
                patterns=[],
                overall_risk=RiskLevel.LOW,
                score=10.0,
                total_patterns=0,
                active_alerts=0,
                high_confidence=0,
                validated_patterns=0,
                highest_confidence=0.0,
                average_confidence=0.0,
            ),
            version=5,
        )
        
        assert aggregate.version == 5
        assert not aggregate.has_pending_events()
    
    def test_pull_consumes_events(self):
        aggregate = CaseIntelligenceAggregate(case_id=CaseId.generate())
        
        analysis = FraudAnalysis(
            case_id=str(uuid4()),
            patterns=[],
            overall_risk=RiskLevel.LOW,
            score=10.0,
            total_patterns=0,
            active_alerts=0,
            high_confidence=0,
            validated_patterns=0,
            highest_confidence=0.0,
            average_confidence=0.0,
        )
        aggregate.record_analysis(analysis)
        
        events1 = aggregate.pull_domain_events()
        assert len(events1) == 1
        
        events2 = aggregate.pull_domain_events()
        assert len(events2) == 0
        assert not aggregate.has_pending_events()
    
    def test_clear_events_without_pull(self):
        aggregate = CaseIntelligenceAggregate(case_id=CaseId.generate())
        
        analysis = FraudAnalysis(
            case_id=str(uuid4()),
            patterns=[],
            overall_risk=RiskLevel.LOW,
            score=10.0,
            total_patterns=0,
            active_alerts=0,
            high_confidence=0,
            validated_patterns=0,
            highest_confidence=0.0,
            average_confidence=0.0,
        )
        aggregate.record_analysis(analysis)
        
        aggregate.clear_events()
        assert not aggregate.has_pending_events()
    
    def test_version_persisted_after_events(self):
        aggregate = CaseIntelligenceAggregate(case_id=CaseId.generate())
        
        analysis = FraudAnalysis(
            case_id=str(uuid4()),
            patterns=[],
            overall_risk=RiskLevel.LOW,
            score=10.0,
            total_patterns=0,
            active_alerts=0,
            high_confidence=0,
            validated_patterns=0,
            highest_confidence=0.0,
            average_confidence=0.0,
        )
        aggregate.record_analysis(analysis)
        
        version = aggregate.version
        
        # Rehydrate from the same version
        rehydrated = CaseIntelligenceAggregate.rehydrate(
            case_id=aggregate.case_id,
            fraud=aggregate.latest_fraud,
            version=version,
        )
        
        assert rehydrated.version == version