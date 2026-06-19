from collections import defaultdict


class EntityMemory:

    def __init__(self):
        self.history = defaultdict(list)

    def add_score(
        self,
        entity_id,
        risk_score,
        trust_score
    ):

        self.history[entity_id].append({
            "risk_score": risk_score,
            "trust_score": trust_score
        })

    def get_history(
        self,
        entity_id
    ):
        return self.history.get(entity_id, [])

    def risk_trend(
        self,
        entity_id
    ):

        history = self.history.get(entity_id, [])

        if len(history) < 2:
            return "UNKNOWN"

        first = history[0]["risk_score"]
        last = history[-1]["risk_score"]

        if last > first:
            return "UP"

        elif last < first:
            return "DOWN"

        return "STABLE"