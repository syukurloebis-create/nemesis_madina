from backend.intelligence.core.anomaly_engine import (
    AnomalyEngine
)


class TestAnomalyEngine:

    def test_detect_outlier(self):

        events = [
            {"payload": {"pagu": 1000000}},
            {"payload": {"pagu": 1200000}},
            {"payload": {"pagu": 900000}},
            {"payload": {"pagu": 50000000}}
        ]

        result = (
            AnomalyEngine()
            .detect(events)
        )

        assert result["anomaly_score"] > 0