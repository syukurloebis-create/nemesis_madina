"""
Event Store - SINGLE SOURCE OF TRUTH
Semua operasi event sourcing harus melalui file ini.
"""

import uuid
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

import hashlib
import json
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, desc

from backend.models.event import Event

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from backend.cases.models import Case

# ============================================
# HASHING UTILITIES
# ============================================

def canonical_json(obj: Any) -> str:
    """Deterministic JSON serialization for consistent hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))

def compute_event_hash(
    case_id: str,
    event_id: str,
    event_type: str,
    version: int,
    data: Dict,
    previous_hash: Optional[str] = None
) -> str:
    """
    Compute SHA256 hash for an event.
    Formula: case_id|event_id|event_type|version|canonical_data|previous_hash
    """
    canonical_data = canonical_json(data)
    content = f"{case_id}|{event_id}|{event_type}|{version}|{canonical_data}|{previous_hash or '0'}"
    return hashlib.sha256(content.encode()).hexdigest()


# ============================================
# CORE EVENT STORE OPERATIONS
# ============================================

async def append_event(
    session: AsyncSession,
    case_id: UUID,
    event_type: str,
    data: Dict,
    previous_hash: Optional[str] = None,
    created_by: Optional[UUID] = None,
    version: Optional[int] = None,
    tenant_id: Optional[UUID] = None
) -> Event:
    """Append a new event to the immutable chain."""
    
    if version is None:
        last_event = await get_last_event(session, case_id)
        version = (
            last_event.event_version + 1
            if last_event
            else 1
        )
    
    # ============================================================
    # FIX: Satu UUID untuk hash dan database
    # ============================================================
    event_uuid = uuid.uuid4()
    event_id = str(event_uuid)
    
    event_hash = compute_event_hash(
        case_id=str(case_id),
        event_id=event_id,  # ← UUID yang sama!
        event_type=event_type,
        version=version,
        data=data,
        previous_hash=previous_hash
    )
    
    event = Event(
        id=event_uuid,  # ← UUID yang sama!
        aggregate_id=case_id,
        aggregate_type="CASE",
        event_type=event_type,
        event_version=version,
        payload=data,
        event_hash=event_hash,
        previous_hash=previous_hash,
        created_by=created_by,
        tenant_id=tenant_id or uuid.uuid4()
    )
    
    session.add(event)
    await session.flush()
    return event


async def get_last_event(
    session: AsyncSession,
    case_id: str
) -> Optional[Event]:
    """Get the most recent event for a case (end of chain)."""
    result = await session.execute(
        select(Event)
        .where(Event.aggregate_id == case_id)
        .order_by(desc(Event.event_version))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_case_events(
    session: AsyncSession,
    case_id: str,
    from_version: Optional[int] = None,
    to_version: Optional[int] = None,
    limit: Optional[int] = None,
    offset: int = 0
) -> List[Event]:
    """
    Get all events for a case in version order.
    This is the SINGLE SOURCE OF TRUTH for reading events.
    """
    query = select(Event).where(Event.aggregate_id == case_id).order_by(Event.event_version)
    
    if from_version is not None:
        query = query.where(Event.event_version >= from_version)
    if to_version is not None:
        query = query.where(Event.event_version <= to_version)
    if limit is not None:
        query = query.offset(offset).limit(limit)
    
    result = await session.execute(query)
    return list(result.scalars().all())


async def validate_chain(events: List[Event]) -> Tuple[bool, Optional[int]]:
    """Validate the integrity of the hash chain."""
    for i, event in enumerate(events):
        # ============================================================
        # FIX: Gunakan event.id, bukan event.event_id
        # ============================================================
        computed = compute_event_hash(
            case_id=event.aggregate_id,
            event_id=str(event.id),  # ← Gunakan event.id!
            event_type=event.event_type,
            version=event.event_version,
            data=event.payload,
            previous_hash=event.previous_hash
        )
        if computed != event.event_hash:
            return False, i
        
        # Check chain linkage
        if i > 0 and event.previous_hash != events[i-1].event_hash:
            return False, i
    
    return True, None


# ============================================
# REPLAY ENGINE (Cached)
# ============================================

class ReplayCache:
    def __init__(self):
        self._cache = {}
        self._version_cache = {}

    def get_state(self, case_id: str, version: int):
        return self._cache.get(f"{case_id}:{version}")

    def set_state(self, case_id: str, version: int, state: dict):
        self._cache[f"{case_id}:{version}"] = state
        self._version_cache[case_id] = max(
            self._version_cache.get(case_id, 0),
            version
        )

    def get_latest_version(self, case_id: str):
        return self._version_cache.get(case_id, 0)

    def invalidate(self, case_id: str):
        keys_to_delete = [k for k in self._cache if k.startswith(f"{case_id}:")]
        for k in keys_to_delete:
            del self._cache[k]
        self._version_cache.pop(case_id, None)

    @staticmethod
    def load_events(session, case_id: str):
        return (
            session.query(Event)
            .filter(Event.aggregate_id == case_id)
            .order_by(Event.created_at.asc())
            .all()
        )


# Global cache instance
_replay_cache = ReplayCache()


async def rebuild_state(
    session: AsyncSession,
    case_id: str,
    target_version: Optional[int] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Rebuild aggregate state from events.
    Menggunakan incremental cache untuk optimasi.
    """
    # Check cache
    if use_cache and target_version is not None:
        cached = _replay_cache.get_state(case_id, target_version)
        if cached:
            return cached
    
    # Get events
    events = await get_case_events(session, case_id, to_version=target_version)
    
    if not events:
        return {
            "case_id": case_id,
            "version": 0,
            "title": None,
            "description": None,
            "status": "OPEN",
            "priority": "MEDIUM",
            "assigned_to": None,
            "evidence_list": [],
            "replay_method": "INCREMENTAL_CACHE"
        }
    
    # Build state from events
    state = {
        "case_id": case_id,
        "version": 0,
        "title": None,
        "description": None,
        "status": "OPEN",
        "priority": "MEDIUM",
        "assigned_to": None,
        "evidence_list": []
    }
    
    for event in events:
        state["version"] = event.event_version
        data = event.payload
        
        if event.event_type == "case_created":
            state["title"] = data.get("title")
            state["description"] = data.get("description")
            state["priority"] = data.get("priority", "MEDIUM")
        elif event.event_type == "status_changed":
            state["status"] = data.get("status", state["status"])
        elif event.event_type == "priority_changed":
            state["priority"] = data.get("priority", state["priority"])
        elif event.event_type == "case_assigned":
            state["assigned_to"] = data.get("assigned_to")
        elif event.event_type == "evidence_added":
            state["evidence_list"].append(data.get("evidence_id"))
    
    # Cache result
    if use_cache:
        _replay_cache.set_state(case_id, state["version"], state.copy())
    
    return state


async def get_state_at_timestamp(
    session: AsyncSession,
    case_id: str,
    timestamp: datetime
) -> Dict[str, Any]:
    """
    Time-travel: Get state at specific timestamp.
    """
    events = await session.execute(text("""
        SELECT event_id, event_type, version, event_hash, previous_hash, 
               timestamp, user_id, data
        FROM events
        WHERE case_id = CAST(:case_id AS UUID) AND timestamp <= :timestamp
        ORDER BY version ASC
    """), {"case_id": case_id, "timestamp": timestamp})
    
    rows = events.fetchall()
    
    if not rows:
        return {
            "case_id": case_id,
            "version": 0,
            "message": "No events found before timestamp",
            "timestamp": timestamp.isoformat()
        }
    
    state = {
        "case_id": case_id,
        "version": 0,
        "title": None,
        "description": None,
        "status": "OPEN",
        "priority": "MEDIUM",
        "assigned_to": None
    }
    
    for row in rows:
        state["version"] = row[2]
        data = row[7]
        
        if row[1] == "case_created":
            state["title"] = data.get("title")
            state["description"] = data.get("description")
            state["priority"] = data.get("priority", "MEDIUM")
        elif row[1] == "status_changed":
            state["status"] = data.get("status", state["status"])
        elif row[1] == "priority_changed":
            state["priority"] = data.get("priority", state["priority"])
        elif row[1] == "case_assigned":
            state["assigned_to"] = data.get("assigned_to")
    
    return state


async def get_event_diff(
    session: AsyncSession,
    case_id: str,
    version_a: int,
    version_b: int
) -> Dict[str, Any]:
    """
    Compare two versions and return differences.
    """
    state_a = await rebuild_state(session, case_id, version_a)
    state_b = await rebuild_state(session, case_id, version_b)
    
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
        "diff": diff,
        "has_changes": len(diff) > 0
    }


# ============================================
# TEMPORAL QUERY ENGINE (Time Travel Debug)
# ============================================

class TemporalQueryEngine:
    """Time-travel query engine untuk forensic debugging."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_state_at_time(self, case_id: str, timestamp: datetime) -> Dict[str, Any]:
        """Get state at specific point in time."""
        return await get_state_at_timestamp(self.session, case_id, timestamp)
    
    async def get_event_stream(
        self,
        case_id: str,
        from_version: Optional[int] = None,
        to_version: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get event stream between versions."""
        events = await get_case_events(self.session, case_id, from_version, to_version)
        return [
            {
                "version": e.event_version,  # ← e.version → e.event_version
                "event_type": e.event_type,
                "timestamp": e.created_at.isoformat() if e.created_at else None,  # ← e.timestamp → e.created_at
                "user_id": e.created_by,  # ← e.user_id → e.created_by
                "data": e.payload,  # ← e.data → e.payload
                "event_hash": e.event_hash,
                "previous_hash": e.previous_hash
            }
            for e in events
        ]
    
    async def trace_chain(self, case_id: str) -> Dict[str, Any]:
        """Trace the entire hash chain for debugging."""
        events = await get_case_events(self.session, case_id)
        
        chain = []
        is_valid = True
        broken_at = None
        
        for i, event in enumerate(events):
            chain.append({
                "position": i,
                "version": event.event_version,
                "event_type": event.event_type,
                "event_hash": event.event_hash,
                "previous_hash": event.previous_hash,
                "valid": i == 0 or event.previous_hash == events[i-1].event_hash
            })
            if i > 0 and event.previous_hash != events[i-1].event_hash:
                is_valid = False
                broken_at = i
        
        return {
            "case_id": case_id,
            "chain_valid": is_valid,
            "total_events": len(events),
            "broken_at_position": broken_at,
            "chain": chain
        }
    
    async def timeline_debug(self, case_id: str) -> Dict[str, Any]:
        """Debug timeline with state changes."""
        events = await self.get_event_stream(case_id)
        timeline = []
        
        for i, event in enumerate(events):
            timeline.append({
                "sequence": i + 1,
                "version": event["version"],
                "event": event["event_type"],
                "timestamp": event["timestamp"],
                "user": event["user_id"],
                "data_summary": ", ".join([f"{k}={v}" for k, v in event["data"].items()][:3])
            })
        
        return {
            "case_id": case_id,
            "total_events": len(events),
            "timeline": timeline,
            "integrity": await self.trace_chain(case_id)
        }


# ============================================
# DEPENDENCY INJECTION
# ============================================

class EventStore:
    """EventStore wrapper untuk dependency injection."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.temporal = TemporalQueryEngine(session)
    
    async def append(self, case_id: str, event_type: str, data: Dict, created_by: str = None) -> Event:
        last = await get_last_event(self.session, case_id)
        previous_hash = last.event_hash if last else None
        version = (last.event_version + 1) if last else 1
        return await append_event(
            self.session, case_id, event_type, data, previous_hash, created_by, version
        )
    
    async def get_events(self, case_id: str, limit: int = None, offset: int = 0) -> List[Event]:
        return await get_case_events(self.session, case_id, limit=limit, offset=offset)
    
    async def get_last_event(self, case_id: str) -> Optional[Event]:
        return await get_last_event(self.session, case_id)
    
    async def rebuild_state(self, case_id: str, target_version: int = None) -> Dict[str, Any]:
        return await rebuild_state(self.session, case_id, target_version)
    
    async def get_state_at_time(self, case_id: str, timestamp: datetime) -> Dict[str, Any]:
        return await self.temporal.get_state_at_time(case_id, timestamp)
    
    async def trace_chain(self, case_id: str) -> Dict[str, Any]:
        return await self.temporal.trace_chain(case_id)
    
    async def timeline_debug(self, case_id: str) -> Dict[str, Any]:
        return await self.temporal.timeline_debug(case_id)
    
    async def compare_versions(self, case_id: str, version_a: int, version_b: int) -> Dict[str, Any]:
        return await get_event_diff(self.session, case_id, version_a, version_b)


async def get_event_store(session: AsyncSession) -> EventStore:
    """FastAPI dependency untuk EventStore."""
    return EventStore(session)
