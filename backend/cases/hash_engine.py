"""SINGLE HASH ENGINE - One Source of Truth for NEMESIS"""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List


def compute_event_hash(event: Dict[str, Any]) -> str:
    """
    Compute SHA256 hash - SINGLE SOURCE OF TRUTH.
    ONLY accepts dict parameter. NO keyword arguments.
    """
    # Build canonical representation
    canonical = {
        "event_id": event.get("event_id", ""),
        "case_id": event.get("case_id", ""),
        "event_type": event.get("event_type", ""),
        "data": event.get("data", {}),
        "actor": event.get("actor", ""),
        "previous_hash": event.get("previous_hash", "0" * 64)
    }
    
    # Handle timestamp
    ts = event.get("timestamp")
    if ts:
        if hasattr(ts, "isoformat"):
            canonical["timestamp"] = ts.isoformat()
        elif isinstance(ts, str):
            canonical["timestamp"] = ts
        else:
            canonical["timestamp"] = str(ts)
    else:
        canonical["timestamp"] = ""
    
    # Sort data keys for consistency
    if isinstance(canonical["data"], dict):
        canonical["data"] = dict(sorted(canonical["data"].items()))
    
    # Deterministic JSON (no extra spaces)
    event_json = json.dumps(canonical, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(event_json.encode()).hexdigest()


def compute_case_snapshot_hash(case: Dict[str, Any]) -> str:
    """Compute hash of case snapshot."""
    snapshot = {k: v for k, v in case.items() if k not in ["updated_at"]}
    snapshot_json = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(snapshot_json.encode()).hexdigest()


def verify_hash_chain(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify entire hash chain integrity."""
    if not events:
        return {"valid": True, "total_events": 0}
    
    expected_previous = "0" * 64
    
    for i, event in enumerate(events):
        actual_previous = event.get("previous_hash", "")
        if actual_previous != expected_previous:
            return {
                "valid": False,
                "broken_at_index": i,
                "reason": f"previous_hash mismatch at event {i}"
            }
        
        computed = compute_event_hash(event)
        stored = event.get("event_hash", "")
        
        if computed != stored:
            return {
                "valid": False,
                "broken_at_index": i,
                "reason": f"event_hash mismatch at event {i}"
            }
        
        expected_previous = stored
    
    return {
        "valid": True,
        "total_events": len(events),
        "chain_root_hash": expected_previous[:16] + "..."
    }


def generate_genesis_event(case_id: str, title: str, description: str, actor: str = "system") -> Dict:
    """Generate genesis event."""
    import uuid
    
    event = {
        "event_id": str(uuid.uuid4()),
        "case_id": case_id,
        "event_type": "case.created",
        "data": {"title": title, "description": description},
        "actor": actor,
        "timestamp": datetime.now(),
        "previous_hash": "0" * 64
    }
    event["event_hash"] = compute_event_hash(event)
    return event
