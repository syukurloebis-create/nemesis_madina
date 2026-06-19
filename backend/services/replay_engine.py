"""
Unified Replay Engine - Konsolidasi replay, rebuild, historical
Single source of truth untuk event replay dan state reconstruction
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

class UnifiedReplayEngine:
    """Unified engine untuk semua operasi replay dan rekonstruksi state"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # =========================================================
    # EVENT STREAM
    # =========================================================
    
    async def get_event_stream(
        self, 
        case_id: str, 
        from_version: Optional[int] = None,
        to_version: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get event stream untuk replay"""
        query = """
            SELECT version, event_type, event_hash, previous_hash, timestamp, user_id, data
            FROM events
            WHERE case_id = CAST(:case_id AS UUID)
        """
        params = {"case_id": case_id, "limit": limit, "offset": offset}
        
        if from_version:
            query += " AND version >= :from_version"
            params["from_version"] = from_version
        if to_version:
            query += " AND version <= :to_version"
            params["to_version"] = to_version
        
        query += " ORDER BY version ASC LIMIT :limit OFFSET :offset"
        
        result = await self.session.execute(text(query), params)
        rows = result.fetchall()
        
        # Get total count
        count_result = await self.session.execute(
            text("SELECT COUNT(*) FROM events WHERE case_id = CAST(:case_id AS UUID)"),
            {"case_id": case_id}
        )
        total = count_result.scalar() or 0
        
        events = []
        for row in rows:
            events.append({
                "version": row[0],
                "event_type": row[1],
                "event_hash": row[2],
                "previous_hash": row[3],
                "timestamp": row[4].isoformat() if row[4] else None,
                "user_id": row[5],
                "data": row[6]
            })
        
        return {
            "case_id": case_id,
            "total_events": total,
            "events": events,
            "from_version": from_version or 1,
            "to_version": to_version or (events[-1]["version"] if events else 0),
            "limit": limit,
            "offset": offset
        }
    
    # =========================================================
    # STATE RECONSTRUCTION (REBUILD)
    # =========================================================
    
    async def rebuild_state(
        self, 
        case_id: str, 
        target_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """Rebuild case state from events (JSON merge style)"""
        result = await self.session.execute(text("""
            SELECT event_type, data, version
            FROM events
            WHERE case_id = CAST(:case_id AS UUID)
            ORDER BY version ASC
        """), {"case_id": case_id})
        
        events = result.fetchall()
        
        if not events:
            return {
                "case_id": case_id,
                "version": 0,
                "title": None,
                "description": None,
                "status": "OPEN",
                "priority": "MEDIUM",
                "assigned_to": None,
                "message": "No events found"
            }
        
        state = {
            "case_id": case_id,
            "version": 0,
            "title": None,
            "description": None,
            "status": "OPEN",
            "priority": "MEDIUM",
            "assigned_to": None,
            "evidence_count": 0
        }
        
        for event in events:
            if target_version and event[2] > target_version:
                break
            
            state["version"] = event[2]
            data = event[1]
            
            if event[0] == "case_created":
                state["title"] = data.get("title")
                state["description"] = data.get("description")
                state["priority"] = data.get("priority", "MEDIUM")
            elif event[0] == "status_changed":
                state["status"] = data.get("status", state["status"])
            elif event[0] == "priority_changed":
                state["priority"] = data.get("priority", state["priority"])
            elif event[0] == "case_assigned":
                state["assigned_to"] = data.get("assigned_to")
            elif event[0] == "evidence_added":
                state["evidence_count"] += 1
        
        return state
    
    # =========================================================
    # DOMAIN REPLAY (TRUE EVENT SOURCING)
    # =========================================================
    
    async def domain_replay(
        self, 
        case_id: str, 
        target_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """True domain event sourcing replay (bukan JSON merge)"""
        events = await self.get_event_stream(case_id, to_version=target_version, limit=1000)
        
        if events["total_events"] == 0:
            return {
                "case_id": case_id,
                "version": 0,
                "state": {},
                "message": "No events found"
            }
        
        # Apply events in sequence using domain logic
        state = {
            "id": case_id,
            "title": None,
            "description": None,
            "status": "OPEN",
            "priority": "MEDIUM",
            "assigned_to": None,
            "evidence": []
        }
        
        for event in events["events"]:
            data = event["data"]
            
            if event["event_type"] == "case_created":
                state["title"] = data.get("title")
                state["description"] = data.get("description")
                state["priority"] = data.get("priority", "MEDIUM")
            elif event["event_type"] == "status_changed":
                state["status"] = data.get("status", state["status"])
            elif event["event_type"] == "case_assigned":
                state["assigned_to"] = data.get("assigned_to")
        
        return {
            "case_id": case_id,
            "version": events["to_version"],
            "state": state,
            "replay_method": "DOMAIN_EVENT_SOURCING"
        }
    
    # =========================================================
    # REPLAY ANIMATION (STEP BY STEP)
    # =========================================================
    
    async def replay_step_by_step(
        self, 
        case_id: str,
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """Step by step replay untuk animasi"""
        events = await self.get_event_stream(case_id, limit=1000)
        
        steps = []
        current_state = {
            "title": None,
            "description": None,
            "status": "OPEN",
            "priority": "MEDIUM"
        }
        
        for event in events["events"]:
            data = event["data"]
            
            # Apply event to state
            if event["event_type"] == "case_created":
                current_state["title"] = data.get("title")
                current_state["description"] = data.get("description")
                current_state["priority"] = data.get("priority", "MEDIUM")
            elif event["event_type"] == "status_changed":
                current_state["status"] = data.get("status", current_state["status"])
            
            steps.append({
                "step": event["version"],
                "event_type": event["event_type"],
                "event_hash": event["event_hash"],
                "state_after": current_state.copy(),
                "animation_duration": 1000 / speed
            })
        
        return {
            "case_id": case_id,
            "total_steps": len(steps),
            "steps": steps,
            "speed": speed
        }
    
    # =========================================================
    # HISTORICAL RECONSTRUCTION
    # =========================================================
    
    async def get_state_at_time(
        self, 
        case_id: str, 
        timestamp: datetime
    ) -> Dict[str, Any]:
        """Get state at specific historical timestamp"""
        result = await self.session.execute(text("""
            SELECT event_type, data, version, timestamp
            FROM events
            WHERE case_id = CAST(:case_id AS UUID) AND timestamp <= :timestamp
            ORDER BY version ASC
        """), {"case_id": case_id, "timestamp": timestamp})
        
        events = result.fetchall()
        
        if not events:
            return {
                "case_id": case_id,
                "timestamp": timestamp.isoformat(),
                "message": "No events found before this timestamp"
            }
        
        state = {
            "case_id": case_id,
            "title": None,
            "description": None,
            "status": "OPEN",
            "priority": "MEDIUM",
            "version": 0
        }
        
        for event in events:
            state["version"] = event[2]
            data = event[1]
            
            if event[0] == "case_created":
                state["title"] = data.get("title")
                state["description"] = data.get("description")
                state["priority"] = data.get("priority", "MEDIUM")
            elif event[0] == "status_changed":
                state["status"] = data.get("status", state["status"])
        
        return {
            "case_id": case_id,
            "target_timestamp": timestamp.isoformat(),
            "state": state
        }
    
    # =========================================================
    # AUDIT TRAIL
    # =========================================================
    
    async def get_audit_trail(
        self, 
        case_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get complete audit trail for case"""
        result = await self.session.execute(text("""
            SELECT version, event_type, event_hash, timestamp, user_id, data
            FROM events
            WHERE case_id = CAST(:case_id AS UUID)
            ORDER BY version DESC
            LIMIT :limit OFFSET :offset
        """), {"case_id": case_id, "limit": limit, "offset": offset})
        
        rows = result.fetchall()
        
        audit_trail = []
        for row in rows:
            audit_trail.append({
                "version": row[0],
                "action": row[1],
                "hash": row[2],
                "timestamp": row[3].isoformat() if row[3] else None,
                "user": row[4],
                "details": row[5]
            })
        
        return {
            "case_id": case_id,
            "total": len(audit_trail),
            "audit_trail": audit_trail
        }
    
    # =========================================================
    # VERSION COMPARE (REPLAY)
    # =========================================================
    
    async def compare_replay_methods(
        self, 
        case_id: str
    ) -> Dict[str, Any]:
        """Compare JSON merge replay vs Domain replay"""
        json_state = await self.rebuild_state(case_id)
        domain_state = await self.domain_replay(case_id)
        
        return {
            "case_id": case_id,
            "json_merge_replay": json_state,
            "domain_replay": domain_state,
            "differences": self._compare_states(json_state, domain_state.get("state", {}))
        }
    
    def _compare_states(self, state_a: Dict, state_b: Dict) -> Dict:
        """Compare two states and return differences"""
        diff = {}
        all_keys = set(state_a.keys()) | set(state_b.keys())
        
        for key in all_keys:
            val_a = state_a.get(key)
            val_b = state_b.get(key)
            if val_a != val_b:
                diff[key] = {"json_merge": val_a, "domain": val_b}
        
        return diff
