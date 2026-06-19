from backend.intelligence.core.lineage_intelligence import (
    LineageIntelligence
)


class TestLineageIntelligence:

    def test_verified_chain(self):

        events = [
            {
                "event_hash": "abc",
                "rebuilt_hash": "abc"
            },
            {
                "event_hash": "def",
                "rebuilt_hash": "def"
            }
        ]

        result = (
            LineageIntelligence()
            .evaluate(events)
        )

        assert result["lineage_score"] == 1.0