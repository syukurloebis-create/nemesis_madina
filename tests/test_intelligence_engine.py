"""
Integration Test Intelligence Engine
"""

from backend.intelligence.intelligence_engine import IntelligenceEngine


class TestIntelligenceEngine:

    def setup_method(self):
        self.engine = IntelligenceEngine()

    def test_complete_evaluation(self):

        events = [
            {"payload": {"pagu": 100_000_000}},
            {"payload": {"pagu": 120_000_000}},
            {"payload": {"pagu": 110_000_000}},
        ]

        result = self.engine.evaluate(
            entity_id="entity_001",
            events=events,
            anomaly_score=0
        )

        assert "risk_score" in result
        assert "trust_score" in result
        assert "confidence_score" in result

    def test_low_risk_entity(self):

        events = [
            {"payload": {"pagu": 10_000_000}}
            for _ in range(20)
        ]

        result = self.engine.evaluate(
            entity_id="stable_entity",
            events=events,
            anomaly_score=0
        )

        assert result["risk_level"] in [
            "LOW",
            "MEDIUM"
        ]

    def test_high_confidence_entity(self):

        events = [
            {"payload": {"pagu": 100_000_000}}
            for _ in range(30)
        ]

        result = self.engine.evaluate(
            entity_id="trusted_entity",
            events=events,
            anomaly_score=0
        )

        assert result["confidence_level"] == "HIGH"

    def test_anomaly_impacts_risk(self):

        events = [
            {"payload": {"pagu": 100_000_000}}
            for _ in range(10)
        ]

        normal = self.engine.evaluate(
            "entity_normal",
            events,
            anomaly_score=0
        )

        anomalous = self.engine.evaluate(
            "entity_anomaly",
            events,
            anomaly_score=10
        )

        assert (
            anomalous["risk_score"]
            >
            normal["risk_score"]
        )

    def test_empty_events(self):

        result = self.engine.evaluate(
            entity_id="empty",
            events=[],
            anomaly_score=0
        )

        assert result["risk_score"] >= 0
        assert result["trust_score"] >= 0
        assert result["confidence_score"] >= 0