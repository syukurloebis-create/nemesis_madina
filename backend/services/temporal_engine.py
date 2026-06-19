"""
Temporal Intelligence Engine - Unified Temporal Engine
Mengkonsolidasikan: historical, snapshots, replay, rebuild
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import json

class TemporalEngine:
    """Unified Temporal Intelligence Engine"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # =========================================================
    # STATE RECONSTRUCTION
    # =========================================================
    
    async def get_state_at_version(
        self, 
        case_id: str, 
        version: int
    ) -> Optional[Dict[str, Any]]:
        """Get case state at specific version"""
        result = await self.session.execute(text("""
            SELECT event_type, data, version, event_hash, previous_hash, timestamp
            FROM events
            WHERE case_id = CAST(:case_id AS UUID) AND version <= :version
            ORDER BY version ASC
        """), {"case_id": case_id, "version": version})
        
        events = result.fetchall()
        if not events:
            return None
        
        state = {
            "case_id": case_id,
            "version": 0,
            "title": None,
            "description": None,
            "status": "OPEN",
            "priority": "MEDIUM",
            "assigned_to": None,
            "reconstructed_at": datetime.now().isoformat()
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
            elif event[0] == "priority_changed":
                state["priority"] = data.get("priority", state["priority"])
            elif event[0] == "case_assigned":
                state["assigned_to"] = data.get("assigned_to")
        
        return state
    
    async def get_state_at_timestamp(
        self, 
        case_id: str, 
        timestamp: datetime
    ) -> Optional[Dict[str, Any]]:
        """Get case state at specific timestamp (Time Travel)"""
        result = await self.session.execute(text("""
            SELECT event_type, data, version, event_hash, previous_hash, timestamp
            FROM events
            WHERE case_id = CAST(:case_id AS UUID) AND timestamp <= :timestamp
            ORDER BY version ASC
        """), {"case_id": case_id, "timestamp": timestamp})
        
        events = result.fetchall()
        if not events:
            return None
        
        state = {
            "case_id": case_id,
            "version": 0,
            "title": None,
            "description": None,
            "status": "OPEN",
            "priority": "MEDIUM",
            "assigned_to": None,
            "target_timestamp": timestamp.isoformat(),
            "reconstructed_at": datetime.now().isoformat()
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
            elif event[0] == "priority_changed":
                state["priority"] = data.get("priority", state["priority"])
            elif event[0] == "case_assigned":
                state["assigned_to"] = data.get("assigned_to")
        
        return state
    
    # =========================================================
    # TIMELINE & HISTORY
    # =========================================================
    
    async def get_timeline(
        self, 
        case_id: str, 
        limit: int = 50, 
        offset: int = 0,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get forensic timeline for a case"""
        query = """
            SELECT version, event_type, event_hash, previous_hash, timestamp, user_id, data
            FROM events
            WHERE case_id = CAST(:case_id AS UUID)
        """
        params = {"case_id": case_id, "limit": limit, "offset": offset}
        
        if from_date:
            query += " AND timestamp >= :from_date"
            params["from_date"] = from_date
        if to_date:
            query += " AND timestamp <= :to_date"
            params["to_date"] = to_date
        
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
                "type": row[1],
                "event_hash": row[2],
                "previous_hash": row[3],
                "timestamp": row[4].isoformat() if row[4] else None,
                "user_id": row[5],
                "data": row[6]
            })
        
        # Validate chain
        chain_valid = True
        broken_at = None
        for i in range(1, len(events)):
            if events[i]["previous_hash"] != events[i-1]["event_hash"]:
                chain_valid = False
                broken_at = i
                break
        
        return {
            "case_id": case_id,
            "total_events": total,
            "events": events,
            "chain_valid": chain_valid,
            "broken_at_sequence": broken_at,
            "limit": limit,
            "offset": offset
        }
    
    async def get_version_history(self, case_id: str) -> Dict[str, Any]:
        """Get version history summary"""
        result = await self.session.execute(text("""
            SELECT version, event_type, timestamp, user_id
            FROM events
            WHERE case_id = CAST(:case_id AS UUID)
            ORDER BY version ASC
        """), {"case_id": case_id})
        
        events = result.fetchall()
        
        versions = []
        for row in events:
            versions.append({
                "version": row[0],
                "event_type": row[1],
                "timestamp": row[2].isoformat() if row[2] else None,
                "user_id": row[3]
            })
        
        return {
            "case_id": case_id,
            "current_version": versions[-1]["version"] if versions else 0,
            "total_versions": len(versions),
            "history": versions
        }
    
    # =========================================================
    # COMPARE & DIFF
    # =========================================================
    
    async def compare_versions(
        self, 
        case_id: str, 
        version_a: int, 
        version_b: int
    ) -> Dict[str, Any]:
        """Compare two versions of a case"""
        state_a = await self.get_state_at_version(case_id, version_a)
        state_b = await self.get_state_at_version(case_id, version_b)
        
        if not state_a or not state_b:
            return {
                "error": "One or both versions not found",
                "version_a": version_a,
                "version_b": version_b
            }
        
        diff = {}
        all_keys = set(state_a.keys()) | set(state_b.keys())
        
        for key in all_keys:
            val_a = state_a.get(key)
            val_b = state_b.get(key)
            if val_a != val_b:
                diff[key] = {
                    "from": val_a,
                    "to": val_b
                }
        
        return {
            "case_id": case_id,
            "version_a": version_a,
            "version_b": version_b,
            "has_changes": len(diff) > 0,
            "diff": diff,
            "state_a": state_a,
            "state_b": state_b
        }
    
    # =========================================================
    # EVENT STREAM
    # =========================================================
    
    async def replay_events(
        self, 
        case_id: str, 
        from_version: int = 1,
        to_version: Optional[int] = None,
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """Replay events with animation-friendly format"""
        result = await self.session.execute(text("""
            SELECT version, event_type, data, event_hash, previous_hash, timestamp
            FROM events
            WHERE case_id = CAST(:case_id AS UUID)
            AND version >= :from_version
            ORDER BY version ASC
        """), {"case_id": case_id, "from_version": from_version})
        
        events = result.fetchall()
        
        if to_version:
            events = [e for e in events if e[0] <= to_version]
        
        state = {}
        for event in events:
            state["version"] = event[0]
            if event[1] == "case_created":
                state["title"] = event[2].get("title")
                state["description"] = event[2].get("description")
                state["priority"] = event[2].get("priority", "MEDIUM")
            elif event[1] == "status_changed":
                state["status"] = event[2].get("status")
            elif event[1] == "case_assigned":
                state["assigned_to"] = event[2].get("assigned_to")
        
        return {
            "case_id": case_id,
            "total_events": len(events),
            "events": [
                {
                    "version": e[0],
                    "type": e[1],
                    "data": e[2],
                    "event_hash": e[3],
                    "previous_hash": e[4],
                    "timestamp": e[5].isoformat() if e[5] else None
                }
                for e in events
            ],
            "final_state": state,
            "replay_speed": speed
        }
    
    # =========================================================
    # INTEGRITY VERIFICATION
    # =========================================================
    
    async def verify_chain(self, case_id: str) -> Dict[str, Any]:
        """Verify hash chain integrity"""
        result = await self.session.execute(text("""
            SELECT event_hash, previous_hash, version
            FROM events
            WHERE case_id = CAST(:case_id AS UUID)
            ORDER BY version ASC
        """), {"case_id": case_id})
        
        events = result.fetchall()
        
        if not events:
            return {
                "case_id": case_id,
                "valid": True,
                "total_events": 0,
                "message": "No events found"
            }
        
        is_valid = True
        broken_at = None
        
        for i in range(1, len(events)):
            if events[i][1] != events[i-1][0]:
                is_valid = False
                broken_at = i
                break
        
        return {
            "case_id": case_id,
            "valid": is_valid,
            "total_events": len(events),
            "broken_at_sequence": broken_at,
            "first_hash": events[0][0],
            "last_hash": events[-1][0],
            "verification_method": "SHA256"
        }
    
    # =========================================================
    # SNAPSHOT MANAGEMENT
    # =========================================================
    
    async def create_snapshot(self, case_id: str) -> Dict[str, Any]:
        """Create a state snapshot at current version"""
        state = await self.get_state_at_version(case_id, None)
        if not state:
            return {"error": "No events found for case"}
        
        # Get current version
        result = await self.session.execute(text("""
            SELECT MAX(version) FROM events WHERE case_id = CAST(:case_id AS UUID)
        """), {"case_id": case_id})
        current_version = result.scalar() or 0
        
        return {
            "case_id": case_id,
            "snapshot_id": f"snap_{case_id[:8]}_{current_version}",
            "version": current_version,
            "state": state,
            "created_at": datetime.now().isoformat(),
            "message": "Snapshot created successfully"
        }
    
    # =========================================================
    # FORENSIC SUMMARY
    # =========================================================
    
    async def get_forensic_summary(self, case_id: str) -> Dict[str, Any]:
        """Comprehensive forensic summary"""
        timeline = await self.get_timeline(case_id, limit=100)
        integrity = await self.verify_chain(case_id)
        history = await self.get_version_history(case_id)
        current_state = await self.get_state_at_version(case_id, None)
        
        return {
            "case_id": case_id,
            "current_state": current_state,
            "timeline": timeline,
            "integrity": integrity,
            "version_history": history,
            "summary": {
                "total_events": timeline["total_events"],
                "chain_valid": integrity["valid"],
                "current_version": history["current_version"],
                "last_updated": timeline["events"][-1]["timestamp"] if timeline["events"] else None
            }
        }
