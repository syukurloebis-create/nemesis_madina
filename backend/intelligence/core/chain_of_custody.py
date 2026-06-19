class ChainOfCustody:
    """
    Sprint 5 - minimal audit lineage tracker
    """

    def __init__(self, registry):
        self.registry = registry

    def record(self, entity_id, features, risk, trust):
        event = {
            "entity_id": entity_id,
            "features": features,
            "risk": risk,
            "trust": trust
        }

        self.registry.register(event)
        return event

    def get_chain(self):
        return self.registry.get_all()