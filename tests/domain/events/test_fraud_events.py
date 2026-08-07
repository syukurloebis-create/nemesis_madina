"""
NEMESIS Madina - Fraud Events Tests
"""

import pytest
from uuid import uuid4
from typing import Dict, Any

from backend.domain.value_objects.case_id import CaseId
from backend.domain.value_objects.fraud_pattern import (
    FraudPattern,
    FraudPatternType,
    FraudPatternSeverity,
)
from backend.domain.value_objects.fraud_analysis import FraudAnalysis
from backend.domain.value_objects.fraud_payload import FraudPayload
from backend.domain.enums.risk_level import RiskLevel
from backend.domain.events.fraud_events import (
    FraudDetectionCompleted,
    FraudAnalysisRecorded,
)


class TestFraudEvents:
    def test_fraud_payload_to_dict(self):
        case_id = str(uuid4())
        
        pattern = FraudPattern(
            pattern_type=FraudPatternType.COLLUSION,
            severity=FraudPatternSeverity.HIGH,
            confidence=80.0,
            validated=False,
            indicators=["indicator1"],
        )
        
        analysis = FraudAnalysis(
            case_id=case_id,
            patterns=[pattern],
            overall_risk=RiskLevel.CRITICAL,
            score=60.0,
            total_patterns=1,
            active_alerts=1,
            high_confidence=1,
            validated_patterns=0,
            highest_confidence=80.0,
            average_confidence=80.0,
        )
        
        payload = FraudPayload(
            case_id=CaseId(case_id),
            analysis=analysis,
            patterns=(pattern,),
        )

        data = payload.to_dict()
        
        assert data["case_id"] == case_id
        assert data["analysis"]["overall_risk"] == "CRITICAL"
        assert data["analysis"]["score"] == 60.0
        assert len(data["patterns"]) == 1

    def test_fraud_payload_from_dict_round_trip(self):
        case_id = str(uuid4())
        
        pattern = FraudPattern(
            pattern_type=FraudPatternType.COLLUSION,
            severity=FraudPatternSeverity.HIGH,
            confidence=80.0,
            validated=False,
            indicators=["indicator1"],
        )
        
        analysis = FraudAnalysis(
            case_id=case_id,
            patterns=[pattern],
            overall_risk=RiskLevel.CRITICAL,
            score=60.0,
            total_patterns=1,
            active_alerts=1,
            high_confidence=1,
            validated_patterns=0,
            highest_confidence=80.0,
            average_confidence=80.0,
        )
        
        original = FraudPayload(
            case_id=CaseId(case_id),
            analysis=analysis,
            patterns=(pattern,),
        )

        data = original.to_dict()
        restored = FraudPayload.from_dict(data)

        assert restored == original

    def test_fraud_detection_completed_legacy_contract(self):
        case_id = str(uuid4())
        
        pattern = FraudPattern(
            pattern_type=FraudPatternType.COLLUSION,
            severity=FraudPatternSeverity.HIGH,
            confidence=80.0,
            validated=False,
            indicators=["indicator1"],
        )
        
        analysis = FraudAnalysis(
            case_id=case_id,
            patterns=[pattern],
            overall_risk=RiskLevel.LOW,
            score=10.0,
            total_patterns=1,
            active_alerts=0,
            high_confidence=0,
            validated_patterns=0,
            highest_confidence=80.0,
            average_confidence=80.0,
        )
        
        event = FraudDetectionCompleted(
            case_id=CaseId(case_id),
            analysis=analysis,
        )

        assert FraudDetectionCompleted.EVENT_NAME == "FraudDetectionCompleted"
        assert event.event_name == "FraudDetectionCompleted"

        data = event.to_dict()
        assert data["event_name"] == "FraudDetectionCompleted"
        assert data["payload"]["analysis"]["overall_risk"] == "LOW"

    def test_fraud_detection_completed_modern_contract(self):
        case_id = str(uuid4())
        
        pattern = FraudPattern(
            pattern_type=FraudPatternType.COLLUSION,
            severity=FraudPatternSeverity.HIGH,
            confidence=80.0,
            validated=False,
            indicators=["indicator1"],
        )
        
        analysis = FraudAnalysis(
            case_id=case_id,
            patterns=[pattern],
            overall_risk=RiskLevel.LOW,
            score=10.0,
            total_patterns=1,
            active_alerts=0,
            high_confidence=0,
            validated_patterns=0,
            highest_confidence=80.0,
            average_confidence=80.0,
        )
        
        payload = FraudPayload(
            case_id=CaseId(case_id),
            analysis=analysis,
            patterns=(pattern,),
        )
        
        event = FraudDetectionCompleted(
            payload=payload,
        )

        assert FraudDetectionCompleted.EVENT_NAME == "FraudDetectionCompleted"
        assert event.event_name == "FraudDetectionCompleted"

        data = event.to_dict()
        assert data["event_name"] == "FraudDetectionCompleted"
        assert data["payload"]["analysis"]["overall_risk"] == "LOW"

    def test_fraud_analysis_recorded_raises_on_invalid_contract(self):
        with pytest.raises(ValueError, match="requires either"):
            FraudAnalysisRecorded()

        with pytest.raises(ValueError, match="requires either"):
            FraudAnalysisRecorded(case_id=CaseId(str(uuid4())))

        with pytest.raises(ValueError, match="requires either"):
            FraudAnalysisRecorded(analysis=FraudAnalysis(
                case_id=str(uuid4()),
                patterns=[],
                overall_risk=RiskLevel.LOW,
                score=0.0,
                total_patterns=0,
                active_alerts=0,
                high_confidence=0,
                validated_patterns=0,
                highest_confidence=0.0,
                average_confidence=0.0,
            ))