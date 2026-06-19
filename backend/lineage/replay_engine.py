# backend/lineage/replay_engine.py
class ReplayEngine:
    async def replay_events(
        self,
        aggregate_id: str,
        from_sequence: int = 0,
        to_sequence: int = None
    ) -> List[Dict]:
        """Replay events untuk merekonstruksi state"""
        events = await self.event_store.get_events(
            aggregate_id, from_sequence, to_sequence
        )
        
        state = {}
        for event in events:
            state = self.apply_event(state, event)
        
        return state
    
    async def verify_integrity(self, aggregate_id: str) -> bool:
        """Verifikasi hash chain integrity"""
        events = await self.event_store.get_events(aggregate_id)
        
        previous_hash = "0"
        for event in events:
            computed_hash = self._compute_hash(event)
            if computed_hash != event['event_hash']:
                return False
            if event['previous_hash'] != previous_hash:
                return False
            previous_hash = computed_hash
        
        return True