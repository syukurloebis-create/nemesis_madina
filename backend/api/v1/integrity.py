"""
Integrity Verification API
Endpoint untuk verifikasi hash chain dan integritas data
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID

from backend.core.hash.verifier import verify_hash_chain, verify_event_integrity
from backend.core.hash.hasher import UnifiedHasher

router = APIRouter(prefix="/integrity", tags=["integrity"])


@router.get("/verify/aggregate/{aggregate_id}")
async def verify_aggregate_integrity(aggregate_id: str):
    """
    Verify entire aggregate's hash chain integrity
    """
    # Get events from database
    events = await get_events_by_aggregate(aggregate_id)
    
    if not events:
        raise HTTPException(status_code=404, detail=f"Aggregate {aggregate_id} not found")
    
    result = verify_hash_chain(events)
    merkle_root = UnifiedHasher.compute_chain_hash(events) if result.is_valid else None
    
    return {
        "aggregate_id": aggregate_id,
        "verified": result.is_valid,
        "total_events": result.total_events,
        "merkle_root": merkle_root,
        "first_broken_index": result.first_broken_index if not result.is_valid else None,
        "broken_reason": result.broken_reason if not result.is_valid else None,
        "verified_at": result.verified_at.isoformat()
    }


@router.get("/verify/event/{event_id}")
async def verify_event_integrity_endpoint(event_id: str):
    """
    Verify single event integrity
    """
    event = await get_event_by_id(event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    
    is_valid, error = verify_event_integrity(event)
    
    return {
        "event_id": event_id,
        "verified": is_valid,
        "error": error if not is_valid else None,
        "aggregate_id": event.get('aggregate_id'),
        "sequence_num": event.get('sequence_num'),
        "event_type": event.get('event_type')
    }


@router.get("/verify/evidence/{evidence_id}")
async def verify_evidence_integrity(evidence_id: UUID):
    """
    Verify evidence integrity
    """
    evidence = await get_evidence_by_id(evidence_id)
    
    if not evidence:
        raise HTTPException(status_code=404, detail=f"Evidence {evidence_id} not found")
    
    # In production, retrieve actual content and compare hash
    # For now, return status
    return {
        "evidence_id": str(evidence_id),
        "verified": evidence.get('is_verified', False),
        "hash": evidence.get('sha256_hash', 'N/A'),
        "source_system": evidence.get('source_system'),
        "verified_at": evidence.get('verified_at')
    }


@router.get("/chain/{aggregate_id}")
async def get_hash_chain(aggregate_id: str, limit: int = 100):
    """
    Get hash chain for aggregate
    """
    events = await get_events_by_aggregate(aggregate_id, limit)
    
    if not events:
        raise HTTPException(status_code=404, detail=f"Aggregate {aggregate_id} not found")
    
    chain = []
    for event in events:
        chain.append({
            "sequence": event.get('sequence_num'),
            "event_type": event.get('event_type'),
            "event_hash": event.get('event_hash'),
            "previous_hash": event.get('previous_hash'),
            "timestamp": event.get('occurred_at')
        })
    
    return {
        "aggregate_id": aggregate_id,
        "chain_length": len(chain),
        "chain": chain,
        "root_hash": UnifiedHasher.compute_chain_hash(events)
    }


@router.get("/statistics")
async def get_integrity_statistics():
    """
    Get overall integrity statistics
    """
    # Get statistics from database
    stats = await get_integrity_stats()
    
    return {
        "total_events": stats.get('total_events', 0),
        "verified_events": stats.get('verified_events', 0),
        "broken_chains": stats.get('broken_chains', 0),
        "integrity_score": stats.get('integrity_score', 0),
        "last_verified": stats.get('last_verified')
    }


# Mock database functions - replace with actual implementations
async def get_events_by_aggregate(aggregate_id: str, limit: int = 100):
    """Get events by aggregate ID - implement with actual DB"""
    # This should query PostgreSQL event_lineage table
    return []

async def get_event_by_id(event_id: str):
    """Get event by ID - implement with actual DB"""
    return None

async def get_evidence_by_id(evidence_id: UUID):
    """Get evidence by ID - implement with actual DB"""
    return None

async def get_integrity_stats():
    """Get integrity statistics - implement with actual DB"""
    return {}
