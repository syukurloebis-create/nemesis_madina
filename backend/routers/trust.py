from fastapi import APIRouter, HTTPException, Query
import sqlite3
import os
from datetime import datetime

router = APIRouter(prefix="/trust", tags=["trust"])


@router.get("/history/{entity_id}")
async def get_trust_history(
    entity_id: str,
    limit: int = Query(50, ge=1, le=200),
):
    """Get trust history for an entity."""
    db_path = os.getenv("SQLITE_PATH", "./nemesis.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT timestamp, old_score, new_score, reason, evidence
        FROM trust_audit_log
        WHERE entity_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (entity_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "timestamp": datetime.fromtimestamp(row["timestamp"]).isoformat(),
            "old_score": row["old_score"],
            "new_score": row["new_score"],
            "reason": row["reason"],
            "evidence": row["evidence"],
        })
    
    return history


@router.get("/history/list")
async def list_trust_history(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List all trust history entries."""
    db_path = os.getenv("SQLITE_PATH", "./nemesis.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT entity_id, timestamp, old_score, new_score, reason
        FROM trust_audit_log
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
