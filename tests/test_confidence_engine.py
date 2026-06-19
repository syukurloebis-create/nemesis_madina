"""
Unit Test Confidence Engine
"""

from backend.intelligence.core.confidence_model import ConfidenceModel


class TestConfidenceModel:

    def setup_method(self):
        self.model = ConfidenceModel()

    def test_single_event_low_confidence(self):

        features = {
            "event_count": 1
        }

        result = self.model.compute(features)

        assert result["confidence_level"] == "LOW"
        assert result["confidence_score"] == 0.30

    def test_five_events_low_confidence(self):

        features = {
            "event_count": 5
        }

        result = self.model.compute(features)

        assert result["confidence_level"] == "LOW"
        assert result["confidence_score"] == 0.50

    def test_medium_confidence(self):

        features = {
            "event_count": 10
        }

        result = self.model.compute(features)

        assert result["confidence_level"] == "MEDIUM"
        assert result["confidence_score"] == 0.70

    def test_high_confidence(self):

        features = {
            "event_count": 25
        }

        result = self.model.compute(features)

        assert result["confidence_level"] == "HIGH"
        assert result["confidence_score"] == 0.90

    def test_missing_event_count(self):

        result = self.model.compute({})

        assert result["confidence_level"] == "LOW"
        assert result["confidence_score"] == 0.30