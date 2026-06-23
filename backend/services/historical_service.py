from cases.event_store import get_state_at_timestamp, get_event_diff

class HistoricalService:
    """Historical reconstruction service."""
    
    def __init__(self, session):
        self.session = session
    
    async def get_state_at_timestamp(self, case_id: str, timestamp):
        return await get_state_at_timestamp(self.session, case_id, timestamp)
    
    async def compare_versions(self, case_id: str, version_a: int, version_b: int):
        return await get_event_diff(self.session, case_id, version_a, version_b)
