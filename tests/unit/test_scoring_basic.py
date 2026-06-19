"""
Basic scoring tests
"""

import pytest


class TestScoringBasic:
    """Basic scoring functionality tests"""
    
    def test_risk_score_range(self):
        """Test that risk scores are within valid range"""
        from backend.intelligence.ml.scoring import RiskScorer
        
        scorer = RiskScorer()
        score = scorer.compute_score({"anomaly_score": 0.5})
        assert 0 <= score <= 1
    
    def test_risk_score_high(self):
        """Test high risk score"""
        from backend.intelligence.ml.scoring import RiskScorer
        
        scorer = RiskScorer()
        score = scorer.compute_score({
            "anomaly_score": 0.9,
            "collusion_risk": 0.9,
            "historical_risk": 0.8
        })
        assert score > 0.5
    
    def test_risk_score_low(self):
        """Test low risk score"""
        from backend.intelligence.ml.scoring import RiskScorer
        
        scorer = RiskScorer()
        score = scorer.compute_score({
            "anomaly_score": 0.1,
            "collusion_risk": 0.1,
            "historical_risk": 0.1
        })
        assert score < 0.5
    
    def test_severity_levels(self):
        """Test severity classification"""
        from backend.intelligence.ml.scoring import RiskScorer
        
        scorer = RiskScorer()
        assert scorer.get_severity(0.9) == "critical"
        assert scorer.get_severity(0.7) == "high"
        assert scorer.get_severity(0.5) == "medium"
        assert scorer.get_severity(0.3) == "low"
        assert scorer.get_severity(0.1) == "info"
