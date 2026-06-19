from backend.intelligence.core.entity_memory import EntityMemory


class TestEntityMemory:

    def test_trend_up(self):

        mem = EntityMemory()

        mem.add_score("A", 0.2, 0.8)
        mem.add_score("A", 0.5, 0.6)

        assert mem.risk_trend("A") == "UP"

    def test_trend_down(self):

        mem = EntityMemory()

        mem.add_score("A", 0.6, 0.5)
        mem.add_score("A", 0.2, 0.8)

        assert mem.risk_trend("A") == "DOWN"

    def test_unknown(self):

        mem = EntityMemory()

        mem.add_score("A", 0.5, 0.5)

        assert mem.risk_trend("A") == "UNKNOWN"