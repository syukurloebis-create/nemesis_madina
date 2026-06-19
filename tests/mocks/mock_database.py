class MockDatabase:
    """Mock database untuk testing tanpa koneksi real."""
    
    def __init__(self):
        self.events = []
        self.edges = []
    
    async def insert_event(self, event: dict):
        self.events.append(event)
    
    async def get_events_by_aggregate(self, aggregate_id: str):
        return [e for e in self.events if e.get("aggregate_id") == aggregate_id]
    
    async def insert_edge(self, edge: dict):
        self.edges.append(edge)
    
    async def get_edges_by_source(self, source_id: str):
        return [e for e in self.edges if e.get("source_id") == source_id]
