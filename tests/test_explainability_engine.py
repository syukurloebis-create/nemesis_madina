from backend.intelligence.core.explainability_engine import (
    ExplainabilityEngine
)


class TestExplainabilityEngine:

    def setup_method(self):
        self.engine = ExplainabilityEngine()

    def test_basic_explanation(self):

        features = {
            "avg_pagu": 1_000_000_000,
            "pagu_coef_var": 0.4,
            "event_count": 5,
            "has_large_pagu": 1
        }

        result = self.engine.explain(
            features,
            risk_score=0.55,
            confidence_score=0.85
        )

        assert len(result.top_factors) > 0

    def test_summary_exists(self):

        features = {
            "avg_pagu": 500_000_000,
            "event_count": 10
        }

        result = self.engine.explain(
            features,
            risk_score=0.40,
            confidence_score=0.75
        )

        assert len(result.summary) > 10

    def test_sorted_contributions(self):

        features = {
            "avg_pagu": 2_000_000_000,
            "pagu_coef_var": 0.1,
            "event_count": 20,
            "has_large_pagu": 1
        }

        result = self.engine.explain(
            features,
            risk_score=0.60,
            confidence_score=0.90
        )

        contributions = [
            x.contribution
            for x in result.top_factors
        ]

        assert contributions == sorted(
            contributions,
            reverse=True
        )