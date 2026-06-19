from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from typing import Optional

router = APIRouter(prefix="/api/v1/evidence", tags=["evidence"])

@router.get("/stats")
async def get_evidence_stats(db: AsyncSession = Depends(get_db)):
    """Get evidence statistics"""
    try:
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'verified' THEN 1 END) as verified,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected,
                ROUND(AVG(trust_score), 2) as avg_trust
            FROM evidence
        """))
        row = result.fetchone()
        return {
            "total": row[0] or 0,
            "verified": row[1] or 0,
            "pending": row[2] or 0,
            "rejected": row[3] or 0,
            "avg_trust": float(row[4]) if row[4] else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top")
async def get_top_evidence(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get top evidence by trust score"""
    try:
        result = await db.execute(text("""
            SELECT 
                id,
                filename,
                status,
                trust_score,
                confidence_level,
                scoring_detail,
                case_id,
                uploaded_at
            FROM evidence
            WHERE trust_score IS NOT NULL
            ORDER BY trust_score DESC
            LIMIT :limit
        """), {"limit": limit})
        rows = result.fetchall()
        return [
            {
                "id": row[0],
                "filename": row[1],
                "status": row[2],
                "trust_score": float(row[3]) if row[3] else 0,
                "confidence_level": row[4] or "LOW",
                "scoring_detail": row[5] or {},
                "case_id": row[6],
                "uploaded_at": row[7].isoformat() if row[7] else None
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/distribution")
async def get_evidence_distribution(db: AsyncSession = Depends(get_db)):
    """Get evidence trust score distribution"""
    try:
        result = await db.execute(text("""
            SELECT 
                CASE 
                    WHEN trust_score >= 80 THEN 'HIGH'
                    WHEN trust_score >= 60 THEN 'MEDIUM'
                    WHEN trust_score >= 40 THEN 'LOW'
                    ELSE 'VERY_LOW'
                END as level,
                COUNT(*) as count,
                ROUND(AVG(trust_score), 2) as avg_score
            FROM evidence
            WHERE trust_score IS NOT NULL
            GROUP BY level
            ORDER BY avg_score DESC
        """))
        rows = result.fetchall()
        return [
            {
                "level": row[0],
                "count": row[1],
                "avg_score": float(row[2]) if row[2] else 0
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-case/{case_id}")
async def get_evidence_by_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get evidence by case"""
    try:
        result = await db.execute(text("""
            SELECT 
                id,
                filename,
                status,
                trust_score,
                confidence_level,
                file_type,
                uploaded_at
            FROM evidence
            WHERE case_id = :case_id
            ORDER BY trust_score DESC NULLS LAST
        """), {"case_id": case_id})
        rows = result.fetchall()
        return [
            {
                "id": row[0],
                "filename": row[1],
                "status": row[2],
                "trust_score": float(row[3]) if row[3] else 0,
                "confidence_level": row[4] or "LOW",
                "file_type": row[5],
                "uploaded_at": row[6].isoformat() if row[6] else None
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chain/{case_id}")
async def get_chain_of_custody(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get chain of custody for a case"""
    try:
        # Get evidence files with status
        result = await db.execute(text("""
            SELECT 
                status,
                COUNT(*) as count
            FROM evidence
            WHERE case_id = :case_id
            GROUP BY status
        """), {"case_id": case_id})
        rows = result.fetchall()
        
        status_map = {
            'verified': 0,
            'pending': 1,
            'rejected': 2
        }
        
        # Create ordered chain
        chain = [
            {"stage": "UPLOAD", "status": "completed", "count": sum(r[1] for r in rows)},
            {"stage": "VERIFY", "status": "active", "count": next((r[1] for r in rows if r[0] == 'verified'), 0)},
            {"stage": "ANALYZE", "status": "pending", "count": next((r[1] for r in rows if r[0] == 'pending'), 0)},
            {"stage": "FINDING", "status": "pending", "count": 0},
            {"stage": "ARCHIVE", "status": "pending", "count": 0}
        ]
        
        # Update status based on data
        verified_count = next((r[1] for r in rows if r[0] == 'verified'), 0)
        pending_count = next((r[1] for r in rows if r[0] == 'pending'), 0)
        
        if verified_count > 0:
            chain[1]["status"] = "completed"
        if pending_count == 0 and verified_count > 0:
            chain[2]["status"] = "completed"
        
        return {
            "case_id": case_id,
            "chain": chain,
            "integrity": "VALID" if verified_count > 0 else "PENDING"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
