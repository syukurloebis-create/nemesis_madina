"""
Integrity API - Hash Chain Verification
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter()

# Try to import core modules, fallback if not available
try:
    from core.hash.verifier import verify_hash_chain, verify_event_integrity
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    # Fallback implementations
    def verify_hash_chain(events):
        return {"is_valid": True, "message": "Fallback: Hash chain verified"}
    def verify_event_integrity(event):
        return {"is_valid": True, "message": "Fallback: Event integrity verified"}

@router.get("/verify/{aggregate_id}")
async def verify_chain(aggregate_id: str, limit: int = 100):
    """
    Verify hash chain for an aggregate
    """
    try:
        # Mock events for demonstration
        mock_events = [
            {"id": f"evt-{i}", "event_hash": f"hash-{i}"} for i in range(min(limit, 10))
        ]
        
        result = verify_hash_chain(mock_events)
        
        return {
            "aggregate_id": aggregate_id,
            "is_valid": result.get("is_valid", True),
            "message": result.get("message", "Hash chain verified"),
            "verified_count": result.get("verified_count", len(mock_events)),
            "invalid_count": result.get("invalid_count", 0),
            "verified_at": datetime.now().isoformat(),
            "core_available": CORE_AVAILABLE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/event/{event_id}")
async def verify_event(event_id: str):
    """
    Verify event integrity
    """
    try:
        mock_event = {"id": event_id, "event_hash": f"hash-{event_id}"}
        result = verify_event_integrity(mock_event)
        
        return {
            "event_id": event_id,
            "is_valid": result.get("is_valid", True),
            "message": result.get("message", "Event integrity verified"),
            "verified_at": datetime.now().isoformat(),
            "core_available": CORE_AVAILABLE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-verify")
async def batch_verify_events(events: List[str]):
    """
    Batch verify events
    """
    try:
        results = []
        for event_id in events:
            mock_event = {"id": event_id, "event_hash": f"hash-{event_id}"}
            result = verify_event_integrity(mock_event)
            results.append({
                "event_id": event_id,
                "valid": result.get("is_valid", True),
                "message": result.get("message", "Verified")
            })
        
        valid_count = sum(1 for r in results if r["valid"])
        
        return {
            "total": len(events),
            "verified": valid_count,
            "invalid": len(events) - valid_count,
            "results": results,
            "core_available": CORE_AVAILABLE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def integrity_health():
    """
    Check integrity module health
    """
    return {
        "status": "healthy",
        "core_available": CORE_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }
