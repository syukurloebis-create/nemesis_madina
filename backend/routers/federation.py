# backend/routers/federation.py
import asyncio
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException
from backend.models.event import EventEnvelope

router = APIRouter(prefix="/federation", tags=["federation"])


@router.post("/ingest/{tenant_id}")
async def ingest_event(tenant_id: str, request: Request):
    # Validate API key (simplified - in production check database)
    api_key = request.headers.get("X-API-Key")
    if api_key != "secret-key-123":
        raise HTTPException(401, "Invalid API key")
    
    # Parse body
    try:
        raw = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON payload")
    
    event_type = raw.get("type")
    if not event_type:
        raise HTTPException(400, "Missing 'type' field")
    
    payload = raw.get("data", {})
    correlation_id = raw.get("correlation_id", tenant_id)
    aggregate_id = raw.get("aggregate_id", tenant_id)
    
    # Create event envelope
    event = EventEnvelope.create(
        event_type=event_type,
        payload=payload,
        correlation_id=correlation_id,
        aggregate_id=aggregate_id,
        schema_version=raw.get("schema_version", 1),
    )
    
    # Add metadata
    if not hasattr(event, 'metadata') or event.event_metadata is None:
        event.event_metadata = {}
    event.event_metadata["tenant_id"] = tenant_id
    event.event_metadata["ingested_at"] = datetime.now(timezone.utc).isoformat()
    
    # Get event bus
    runtime = request.app.state.runtime
    event_bus = runtime.get("event_bus")
    if not event_bus:
        raise HTTPException(500, "Event bus not available")
    
    # Publish
    subject = f"nemesis.federation.{tenant_id}.events.{event_type}"
    
    # FIX 2: Handle return value properly
    success = await event_bus.publish(subject, event)
    
    if not success:
        raise HTTPException(500, detail="Event publish failed")
    
    return {
        "status": "ingested",
        "event_id": event.event_id,
        "tenant_id": tenant_id,
        "event_type": event_type,
        "subject": subject,
        "publish_status": "success"
    }

@router.get("/verify/{tenant_id}/{aggregate_id}")
async def federated_verify(tenant_id: str, aggregate_id: str, request: Request):
    """Verifikasi trust lineage untuk tenant tertentu."""
    runtime = request.app.state.runtime
    pool = runtime.get("pool")
    
    from core.events.lineage_verifier import LineageVerifier
    verifier = LineageVerifier(pool)
    
    result = await verifier.verify_aggregate_chain(aggregate_id)
    
    return {
        "tenant_id": tenant_id,
        "aggregate_id": aggregate_id,
        "verified": result['verified'],
        "chain_integrity": result['chain_integrity'],
        "total_events": result['total_events'],
        "rebuilt": result.get('rebuilt', False),
        "verified_at": datetime.utcnow().isoformat()
    }
