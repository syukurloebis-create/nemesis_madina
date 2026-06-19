# backend/routers/observability.py
from fastapi import APIRouter, Request, HTTPException

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/event-lineage/{aggregate_id}")
async def event_lineage(aggregate_id: str, request: Request):
    runtime = request.app.state.runtime
    pool = runtime.get("pool")
    
    if not pool:
        raise HTTPException(500, "Database pool not available")
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT event_id, event_type, sequence_num, created_at, event_hash, previous_hash
            FROM event_lineage
            WHERE aggregate_id = $1
            ORDER BY sequence_num ASC
            """,
            aggregate_id
        )
    
    if not rows:
        raise HTTPException(404, f"No events found for aggregate_id {aggregate_id}")
    
    nodes = [{"data": {"id": r["event_id"], "label": r["event_type"], "sequence": r["sequence_num"]}} for r in rows]
    edges = []
    for i in range(len(rows) - 1):
        edges.append({"data": {"source": rows[i]["event_id"], "target": rows[i+1]["event_id"], "label": "next"}})
    
    return {"aggregate_id": aggregate_id, "nodes": nodes, "edges": edges}
