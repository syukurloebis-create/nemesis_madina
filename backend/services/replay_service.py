"""
Replay Service - PURE FUNCTION
Directly uses core event store, NO intermediate service layer.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

# Direct import from core - NO EventStoreService
from backend.cases.event_store import get_case_events
from backend.models.event import Event


class ReplayService:
    """
    Clean Replay Engine.
    - Pure function
    - Direct DB access via core functions
    - NO intermediate service layer
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def replay(
        self,
        case_id: str,
        from_version: int = 0,
        to_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """Replay events to rebuild state"""
        events = await get_case_events(self.db, case_id)
        
        # Filter events based on version
        filtered_events = []
        for event in events:
            event_version = event.event_version if hasattr(event, 'event_version') else getattr(event, 'version', 0)
            
            if from_version > 0 and event_version < from_version:
                continue
            if to_version is not None and event_version > to_version:
                continue
            filtered_events.append(event)
        
        # Reduce events to state
        return self._reduce_events(filtered_events)

    async def get_event_timeline(
        self, 
        case_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get event timeline for a case"""
        events = await get_case_events(self.db, case_id)
        
        timeline = []
        for event in events[offset:offset+limit]:
            timeline.append({
                "id": str(event.id),
                "event_type": event.event_type,
                "version": event.event_version,
                "timestamp": event.created_at.isoformat() if event.created_at else None,
                "payload": event.payload,
                "event_hash": event.event_hash[:16] + "..." if event.event_hash else None
            })
        
        return {
            "case_id": case_id,
            "total_events": len(events),
            "limit": limit,
            "offset": offset,
            "timeline": timeline
        }

    async def get_version_history(self, case_id: str) -> Dict[str, Any]:
        """Get version history with state snapshots"""
        events = await get_case_events(self.db, case_id)
        
        versions = []
        for i, event in enumerate(events, 1):
            versions.append({
                "version": i,
                "event_type": event.event_type,
                "timestamp": event.created_at.isoformat() if event.created_at else None,
                "event_hash": event.event_hash[:16] + "..." if event.event_hash else None
            })
        
        return {
            "case_id": case_id,
            "current_version": len(events),
            "versions": versions
        }

    async def get_state_at_version(
        self, 
        case_id: str, 
        version: int
    ) -> Dict[str, Any]:
        """Get state at specific version"""
        return await self.replay(case_id, to_version=version)

    async def get_state_at_timestamp(
        self, 
        case_id: str, 
        timestamp: str
    ) -> Dict[str, Any]:
        """Get state at specific timestamp"""
        from datetime import datetime
        target_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        events = await get_case_events(self.db, case_id)
        events_before = [e for e in events if e.created_at <= target_time]
        
        return self._reduce_events(events_before)

    async def compare_versions(
        self,
        case_id: str,
        version_a: int,
        version_b: int
    ) -> Dict[str, Any]:
        """Compare state between two versions"""
        state_a = await self.get_state_at_version(case_id, version_a)
        state_b = await self.get_state_at_version(case_id, version_b)

        changes = []
        all_keys = set(state_a.keys()) | set(state_b.keys())
        
        for key in all_keys:
            old_val = state_a.get(key)
            new_val = state_b.get(key)
            if old_val != new_val:
                changes.append({
                    "field": key,
                    "old_value": old_val,
                    "new_value": new_val
                })

        return {
            "version_a": version_a,
            "version_b": version_b,
            "state_a": state_a,
            "state_b": state_b,
            "changes": changes,
            "change_count": len(changes)
        }

    def _reduce_events(self, events: List[Event]) -> Dict[str, Any]:
        """Pure function: reduce events to state"""
        state = {
            "title": None,
            "description": None,
            "status": "DRAFT",
            "priority": "MEDIUM",
            "assigned_to": None,
            "evidence": []
        }

        for event in events:
            event_type = event.event_type
            payload = event.payload or {}

            # Apply event based on type
            if event_type == "CASE_CREATED":
                state["title"] = payload.get("title")
                state["description"] = payload.get("description")
                state["status"] = payload.get("status", "OPEN")
                state["priority"] = payload.get("priority", "MEDIUM")
            elif event_type == "CASE_UPDATED":
                if "title" in payload:
                    state["title"] = payload["title"]
                if "description" in payload:
                    state["description"] = payload["description"]
            elif event_type == "CASE_STATUS_CHANGED":
                state["status"] = payload.get("new_status", state["status"])
            elif event_type == "CASE_ASSIGNED":
                state["assigned_to"] = payload.get("assigned_to")
            elif event_type == "EVIDENCE_ADDED":
                state["evidence"].append(payload)
            else:
                # Generic merge for unknown event types
                for key, value in payload.items():
                    if key not in ["event_type", "timestamp"]:
                        state[key] = value

        return state


# Factory function untuk dependency injection
def create_replay_service(db: AsyncSession) -> ReplayService:
    """Factory untuk ReplayService"""
    return ReplayService(db)

    async def get_state_at_timestamp(
        self, 
        case_id: str, 
        timestamp_str: str
    ) -> Dict[str, Any]:
        """Get case state at specific timestamp (Time Travel)"""
        from datetime import datetime
        target_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        events = await get_case_events(self.db, case_id)
        events_before = [e for e in events if e.created_at <= target_time]
        
        if not events_before:
            return {
                "case_id": case_id,
                "timestamp": timestamp_str,
                "state": {},
                "events_found": 0
            }
        
        state = self._reduce_events(events_before)
        
        return {
            "case_id": case_id,
            "timestamp": timestamp_str,
            "state": state,
            "events_applied": len(events_before),
            "last_version": events_before[-1].event_version
        }
