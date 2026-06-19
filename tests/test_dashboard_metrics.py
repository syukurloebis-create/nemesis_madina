"""
Unit Test Dashboard Metrics
"""

from backend.services.dashboard_metrics import DashboardMetrics


class TestDashboardMetrics:

    def test_empty_results(self):

        result = DashboardMetrics.summarize([])

        assert result["total_entities"] == 0
        assert result["average_trust"] == 0

    def test_single_entity(self):

        data = [
            {
                "risk_level": "LOW",
                "trust_score": 0.80
            }
        ]

        result = DashboardMetrics.summarize(data)

        assert result["total_entities"] == 1
        assert result["low_risk"] == 1

    def test_risk_distribution(self):

        data = [
            {
                "risk_level": "HIGH",
                "trust_score": 0.40
            },
            {
                "risk_level": "MEDIUM",
                "trust_score": 0.60
            },
            {
                "risk_level": "LOW",
                "trust_score": 0.80
            }
        ]

        result = DashboardMetrics.summarize(data)

        assert result["high_risk"] == 1
        assert result["medium_risk"] == 1
        assert result["low_risk"] == 1

    def test_average_trust(self):

        data = [
            {
                "risk_level": "LOW",
                "trust_score": 0.60
            },
            {
                "risk_level": "LOW",
                "trust_score": 0.80
            }
        ]

        result = DashboardMetrics.summarize(data)

        assert result["average_trust"] == 0.70

    def test_multiple_entities(self):

        data = [
            {
                "risk_level": "HIGH",
                "trust_score": 0.40
            }
            for _ in range(10)
        ]

        result = DashboardMetrics.summarize(data)

        assert result["total_entities"] == 10
        assert result["high_risk"] == 10