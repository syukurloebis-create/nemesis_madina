from backend.intelligence.core.graph_intelligence import (
    GraphIntelligence
)


class TestGraphIntelligence:

    def test_empty_graph(self):

        result = GraphIntelligence().analyze([])

        assert result["degree"] == 0

    def test_concentration_detection(self):

        edges = [
            {
                "source_id": "A",
                "target_id": "VENDOR_1"
            },
            {
                "source_id": "A",
                "target_id": "VENDOR_1"
            },
            {
                "source_id": "A",
                "target_id": "VENDOR_1"
            }
        ]

        result = GraphIntelligence().analyze(
            edges
        )

        assert result["risk_flag"] is True