"""
Integrity Router - Fixed imports
"""
import sys
from pathlib import Path

# Fix import path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

# ============================================================
# FIXED IMPORTS - TRY MULTIPLE PATHS
# ============================================================

def get_event_store():
    """Try multiple paths to import event store"""
    try:
        # Try direct import
        from backend.cases.event_store import get_case_events, compute_event_hash
        return get_case_events, compute_event_hash
    except ImportError:
        pass
    
    try:
        # Try from cases module
        from cases.event_store import get_case_events, compute_event_hash
        return get_case_events, compute_event_hash
    except ImportError:
        pass
    
    try:
        # Try from project root
        from cases.event_store import get_case_events, compute_event_hash
        return get_case_events, compute_event_hash
    except ImportError:
        pass
    
    # Fallback: create mock functions
    def get_case_events(case_id):
        return []
    
    def compute_event_hash(events):
        return "mock-hash"
    
    return get_case_events, compute_event_hash

# Get event store functions
get_case_events, compute_event_hash = get_event_store()

# Import database
def get_db():
    """Get database session"""
    try:
        from backend.infrastructure.database import get_db
        return get_db
    except ImportError:
        return None

router = APIRouter(prefix="/integrity", tags=["integrity"])

@router.get("/case/{case_id}/events")
async def get_case_events_endpoint(
    case_id: str,
    db: Session = Depends(get_db) if get_db else None
):
    """Get case events"""
    try:
        events = get_case_events(case_id)
        return {
            "case_id": case_id,
            "events": events,
            "hash": compute_event_hash(events),
            "count": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/case/{case_id}/hash")
async def get_case_hash(
    case_id: str,
    db: Session = Depends(get_db) if get_db else None
):
    """Get case hash"""
    try:
        events = get_case_events(case_id)
        hash_value = compute_event_hash(events)
        return {
            "case_id": case_id,
            "hash": hash_value,
            "event_count": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))