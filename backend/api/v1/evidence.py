# backend/api/v1/evidence.py - Evidence Router (FIXED)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["evidence"])

@router.get("/stats")
async def get_evidence_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get evidence statistics"""
    try:
        result = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'verified' THEN 1 END) as verified,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected
                FROM evidence
            """)
        )
        row = result.fetchone()
        return {
            "total": row[0] or 0,
            "verified": row[1] or 0,
            "pending": row[2] or 0,
            "rejected": row[3] or 0
        }
    except Exception as e:
        logger.error(f"Error getting evidence stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/case/{case_id}")
async def get_evidence_by_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get evidence for a specific case"""
    try:
        result = await db.execute(
            text("""
                SELECT 
                    id, title, file_type, status, 
                    trust_score, created_at, uploaded_at
                FROM evidence 
                WHERE case_id = :case_id
                ORDER BY created_at DESC
            """),
            {"case_id": case_id}
        )
        rows = result.fetchall()
        return [
            {
                "id": row[0],
                "title": row[1],
                "file_type": row[2],
                "status": row[3],
                "trust_score": float(row[4]) if row[4] else 0,
                "created_at": row[5].isoformat() if row[5] else None,
                "uploaded_at": row[6].isoformat() if row[6] else None
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error getting evidence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top")
async def get_top_evidence(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get top evidence by trust score"""
    try:
        result = await db.execute(
            text("""
                SELECT 
                    e.id,
                    e.title,
                    e.trust_score,
                    e.status,
                    e.file_type,
                    e.created_at,
                    c.title as case_title
                FROM evidence e
                LEFT JOIN cases c ON e.case_id = c.id
                WHERE e.trust_score IS NOT NULL
                ORDER BY e.trust_score DESC
                LIMIT :limit
            """),
            {"limit": limit}
        )
        rows = result.fetchall()
        return [
            {
                "id": row[0],
                "title": row[1],
                "trust_score": float(row[2]) if row[2] else 0,
                "status": row[3],
                "file_type": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "case_title": row[6]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error getting top evidence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
