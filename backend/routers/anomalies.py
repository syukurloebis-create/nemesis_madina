# backend/routers/anomalies.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
import sqlite3
import os

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("/")
async def get_anomalies(
    limit: int = Query(50, ge=1, le=200),
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
):
    """Get anomalies from SQLite."""
    db_path = os.getenv("SQLITE_PATH", "./nemesis.db")
    
    if not os.path.exists(db_path):
        return []
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT 
            id, entity_id, anomaly_type, severity, details, 
            detected_at, resolved, confidence, requires_review, evidence
        FROM anomalies
    """
    params = []
    conditions = []
    
    if severity:
        conditions.append("severity = ?")
        params.append(severity)
    if resolved is not None:
        conditions.append("resolved = ?")
        params.append(1 if resolved else 0)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY detected_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    anomalies_list = []
    for row in rows:
        anomaly = dict(row)
        # Convert detected_at to ISO format
        if anomaly.get('detected_at'):
            try:
                anomaly['detected_at'] = datetime.fromtimestamp(
                    float(anomaly['detected_at'])
                ).isoformat()
            except (ValueError, TypeError):
                pass
        anomalies_list.append(anomaly)
    
    return anomalies_list


@router.get("/{anomaly_id}")
async def get_anomaly(anomaly_id: int):
    """Get single anomaly by ID."""
    db_path = os.getenv("SQLITE_PATH", "./nemesis.db")
    
    if not os.path.exists(db_path):
        raise HTTPException(404, "Anomaly not found")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM anomalies WHERE id = ?",
        (anomaly_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(404, "Anomaly not found")
    
    anomaly = dict(row)
    if anomaly.get('detected_at'):
        try:
            anomaly['detected_at'] = datetime.fromtimestamp(
                float(anomaly['detected_at'])
            ).isoformat()
        except (ValueError, TypeError):
            pass
    
    return anomaly
