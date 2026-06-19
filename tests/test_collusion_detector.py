from backend.graph.relationship_graph import RelationshipGraph
from backend.graph.collusion_detector import CollusionDetector


class TestCollusion:

    def test_detection(self):

        graph = RelationshipGraph()

        for i in range(10):
            graph.add_edge(
                "PT_MAJU_JAYA",
                f"PAKET_{i}"
            )

        detector = CollusionDetector()

        findings = detector.detect(
            graph,
            threshold=5
        )

        assert len(findings) == 1

    def test_no_detection(self):

        graph = RelationshipGraph()

        graph.add_edge(
            "PT_A",
            "PAKET_1"
        )

        detector = CollusionDetector()

        findings = detector.detect(
            graph,
            threshold=5
        )

        assert findings == []