# routers/evidence.py - Evidence Endpoints (ROUTE ORDER FIXED)
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func
from typing import Optional
from datetime import datetime
import uuid
import hashlib

from database import get_db

router = APIRouter(prefix="/api/v1/evidence", tags=["evidence"])

# ============================================
# STATIC ROUTES - HARUS DI ATAS /{evidence_id}
# ============================================

@router.get("/stats", response_model=None)
async def get_evidence_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get evidence statistics - CASE INSENSITIVE"""
    try:
        # ============ FIX: Case-insensitive ============
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN LOWER(status) = 'verified' THEN 1 END) as verified,
                COUNT(CASE WHEN LOWER(status) = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN LOWER(status) = 'rejected' THEN 1 END) as rejected,
                AVG(trust_score) as avg_trust
            FROM evidence
        """))
        row = result.fetchone()
        
        return {
            "total": row[0] or 0,
            "verified": row[1] or 0,
            "pending": row[2] or 0,
            "rejected": row[3] or 0,
            "avg_trust_score": float(row[4] or 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_model=None)
async def get_evidence_metrics(
    db: AsyncSession = Depends(get_db)
):
    """Get evidence metrics for risk engine - CASE INSENSITIVE"""
    try:
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN LOWER(status) = 'verified' THEN 1 END) as verified,
                COUNT(CASE WHEN LOWER(status) = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN LOWER(status) = 'rejected' THEN 1 END) as rejected,
                AVG(trust_score) as avg_trust,
                COUNT(CASE WHEN immutable = true THEN 1 END) as immutable_count
            FROM evidence
        """))
        row = result.fetchone()
        
        total = row[0] or 1
        verified = row[1] or 0
        avg_trust = float(row[4] or 0)
        
        return {
            "total": total,
            "verified": verified,
            "pending": row[2] or 0,
            "rejected": row[3] or 0,
            "avg_trust_score": avg_trust,
            "immutable_count": row[5] or 0,
            "verification_ratio": round(verified / total, 3) if total > 0 else 0,
            "quality_score": round((avg_trust / 100) * 0.6 + (verified / total) * 0.4, 3) if total > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quality", response_model=None)
async def get_evidence_quality(
    db: AsyncSession = Depends(get_db)
):
    """Get evidence quality score for dashboard"""
    try:
        from services.evidence_scoring import EvidenceScorer
        
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN LOWER(status) = 'verified' THEN 1 END) as verified,
                COUNT(CASE WHEN LOWER(status) = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN LOWER(status) = 'rejected' THEN 1 END) as rejected,
                AVG(trust_score) as avg_trust,
                COUNT(CASE WHEN immutable = true THEN 1 END) as immutable_count
            FROM evidence
        """))
        row = result.fetchone()
        
        total = row[0] or 1
        verified = row[1] or 0
        avg_trust = float(row[4] or 0)
        immutable_count = row[5] or 0
        
        quality = EvidenceScorer.get_evidence_quality(
            trust_score=avg_trust,
            status="verified",
            verified_count=verified,
            total_evidence=total,
            immutable_count=immutable_count
        )
        
        return {
            "evidence_quality": quality,
            "statistics": {
                "total": total,
                "verified": verified,
                "pending": row[2] or 0,
                "rejected": row[3] or 0,
                "avg_trust_score": round(avg_trust, 2),
                "immutable_count": immutable_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/case/{case_id}", response_model=None)
async def get_evidence_by_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get evidence for a specific case"""
    try:
        result = await db.execute(text("""
            SELECT 
                id, case_id, filename, file_type, LOWER(status) as status,
                trust_score, confidence_level, uploaded_at, updated_at
            FROM evidence 
            WHERE case_id = :case_id
            ORDER BY uploaded_at DESC
        """), {"case_id": case_id})
        rows = result.fetchall()
        
        return [
            {
                "id": str(row[0]),
                "case_id": str(row[1]) if row[1] else None,
                "filename": row[2],
                "file_type": row[3],
                "status": row[4],
                "trust_score": float(row[5]) if row[5] else 0,
                "confidence_level": row[6],
                "uploaded_at": row[7].isoformat() if row[7] else None,
                "updated_at": row[8].isoformat() if row[8] else None
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top", response_model=None)
async def get_top_evidence(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get top evidence by trust score"""
    try:
        result = await db.execute(text("""
            SELECT 
                id, filename, trust_score, LOWER(status) as status,
                file_type, uploaded_at, confidence_level
            FROM evidence 
            WHERE trust_score IS NOT NULL
            ORDER BY trust_score DESC
            LIMIT :limit
        """), {"limit": limit})
        rows = result.fetchall()
        
        return [
            {
                "id": str(row[0]),
                "filename": row[1],
                "trust_score": float(row[2]) if row[2] else 0,
                "status": row[3],
                "file_type": row[4],
                "uploaded_at": row[5].isoformat() if row[5] else None,
                "confidence_level": row[6]
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# DYNAMIC ROUTE - HARUS DI BAWAH STATIC ROUTES
# ============================================

@router.get("/{evidence_id}", response_model=None)
async def get_evidence_by_id(
    evidence_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get evidence by ID"""
    try:
        result = await db.execute(text("""
            SELECT 
                id, case_id, filename, file_type, file_size,
                file_hash, LOWER(status) as status, trust_score, confidence_level,
                uploaded_at, updated_at, verified_at,
                evidence_type, storage_path, immutable
            FROM evidence 
            WHERE id = :id
        """), {"id": evidence_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=404, 
                detail=f"Evidence with ID {evidence_id} not found"
            )
        
        return {
            "id": str(row[0]),
            "case_id": str(row[1]) if row[1] else None,
            "filename": row[2],
            "file_type": row[3],
            "file_size": row[4] or 0,
            "file_hash": row[5],
            "status": row[6] or "pending",
            "trust_score": float(row[7]) if row[7] else 0,
            "confidence_level": row[8],
            "uploaded_at": row[9].isoformat() if row[9] else None,
            "updated_at": row[10].isoformat() if row[10] else None,
            "verified_at": row[11].isoformat() if row[11] else None,
            "evidence_type": row[12],
            "storage_path": row[13],
            "immutable": row[14] or False
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Upload, Verify, Reject, Custody tetap sama
@router.post("/upload", response_model=None)
async def upload_evidence(
    case_id: str = Form(...),
    file: UploadFile = File(...),
    evidence_type: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        evidence_id = str(uuid.uuid4())
        content = await file.read()
        file_hash = hashlib.sha256(content).hexdigest()
        
        await db.execute(text("""
            INSERT INTO evidence (
                id, case_id, filename, file_type,
                file_size, file_hash, status, trust_score,
                confidence_level, uploaded_at, updated_at,
                evidence_type, storage_path, immutable
            ) VALUES (
                :id, :case_id, :filename, :file_type,
                :file_size, :file_hash, 'pending', 0,
                'LOW', NOW(), NOW(),
                :evidence_type, :storage_path, false
            )
        """), {
            "id": evidence_id,
            "case_id": case_id,
            "filename": file.filename,
            "file_type": file.content_type or "unknown",
            "file_size": len(content),
            "file_hash": file_hash,
            "evidence_type": evidence_type or "document",
            "storage_path": f"uploads/{case_id}/{evidence_id}_{file.filename}"
        })
        
        await db.commit()
        
        return {
            "id": evidence_id,
            "case_id": case_id,
            "filename": file.filename,
            "status": "pending",
            "message": "Evidence uploaded successfully"
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{evidence_id}/verify", response_model=None)
async def verify_evidence(
    evidence_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        from services.evidence_scoring import EvidenceScorer
        confidence = EvidenceScorer.calculate_confidence(100, "verified")
        
        result = await db.execute(text("""
            UPDATE evidence 
            SET status = 'verified', 
                verified_at = NOW(),
                trust_score = 100,
                confidence_level = :confidence
            WHERE id = :id
            RETURNING id, status
        """), {"id": evidence_id, "confidence": confidence})
        await db.commit()
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Evidence not found")
        
        return {"id": str(row[0]), "status": row[1], "message": "Evidence verified"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{evidence_id}/reject", response_model=None)
async def reject_evidence(
    evidence_id: str,
    reason: str = Query(..., description="Rejection reason"),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(text("""
            UPDATE evidence 
            SET status = 'rejected', 
                trust_score = 0,
                confidence_level = 'LOW'
            WHERE id = :id
            RETURNING id, status
        """), {"id": evidence_id, "reason": reason})
        await db.commit()
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Evidence not found")
        
        return {"id": str(row[0]), "status": row[1], "message": "Evidence rejected"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{evidence_id}/custody", response_model=None)
async def get_custody_history(
    evidence_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        return [
            {
                "id": "sample-1",
                "evidence_id": evidence_id,
                "action": "UPLOAD",
                "actor": "System",
                "timestamp": datetime.now().isoformat(),
                "notes": "Evidence uploaded",
                "metadata": {}
            }
        ]
    except Exception as e:
        return []

@router.get("/top", response_model=None)
async def get_top_evidence(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get top evidence by trust score - CASE INSENSITIVE"""
    try:
        result = await db.execute(text("""
            SELECT 
                id, filename, trust_score, LOWER(status) as status,
                file_type, uploaded_at, confidence_level
            FROM evidence 
            WHERE trust_score IS NOT NULL
            ORDER BY trust_score DESC
            LIMIT :limit
        """), {"limit": limit})
        rows = result.fetchall()
        
        return [
            {
                "id": str(row[0]),
                "filename": row[1],
                "trust_score": float(row[2]) if row[2] else 0,
                "status": row[3],
                "file_type": row[4],
                "uploaded_at": row[5].isoformat() if row[5] else None,
                "confidence_level": row[6]
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top", response_model=None)
async def get_top_evidence(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get top evidence by trust score - FINAL FIX"""
    try:
        result = await db.execute(text("""
            SELECT 
                id, 
                filename, 
                trust_score, 
                LOWER(status) as status,
                file_type, 
                uploaded_at, 
                confidence_level
            FROM evidence 
            WHERE trust_score IS NOT NULL
            ORDER BY trust_score DESC
            LIMIT :limit
        """), {"limit": limit})
        rows = result.fetchall()
        
        return [
            {
                "id": str(row[0]),
                "filename": row[1],
                "trust_score": float(row[2]) if row[2] else 0,
                "status": row[3],
                "file_type": row[4],
                "uploaded_at": row[5].isoformat() if row[5] else None,
                "confidence_level": row[6]
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph/{case_id}", response_model=None)
async def get_evidence_graph(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get evidence-graph relationship for a case"""
    try:
        # 1. Get evidence data
        evidence_result = await db.execute(text("""
            SELECT 
                id, filename, trust_score, status,
                confidence_level, evidence_type
            FROM evidence 
            WHERE case_id = :case_id
        """), {"case_id": case_id})
        evidence_rows = evidence_result.fetchall()
        
        # 2. Get graph entities (vendors)
        graph_result = await db.execute(text("""
            SELECT 
                id, name, entity_type, risk_score
            FROM graph_entities 
            WHERE case_id = :case_id
            LIMIT 10
        """), {"case_id": case_id})
        graph_rows = graph_result.fetchall()
        
        return {
            "case_id": case_id,
            "evidence_count": len(evidence_rows),
            "evidence": [
                {
                    "id": str(row[0]),
                    "filename": row[1],
                    "trust_score": float(row[2]) if row[2] else 0,
                    "status": row[3],
                    "confidence": row[4],
                    "type": row[5]
                }
                for row in evidence_rows
            ],
            "entities": [
                {
                    "id": str(row[0]),
                    "name": row[1],
                    "type": row[2],
                    "risk_score": float(row[3]) if row[3] else 0
                }
                for row in graph_rows
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
