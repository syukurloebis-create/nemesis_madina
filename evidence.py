from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, List
import uuid
import hashlib
from datetime import datetime

from backend.infrastructure.database import get_db
from backend.security.dependencies import get_current_user

router = APIRouter(prefix="/evidence", tags=["Evidence Management"])


@router.get("/case/{case_id}")
async def get_evidence_by_case(
    case_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db)
):
    """Get all evidence for a specific case"""
    
    result = await session.execute(
        text("""
            SELECT id, filename, sha256_hash, file_size, mime_type,
                   uploaded_by, uploaded_at, verified_at, integrity_status
            FROM evidence_files
            WHERE case_id = :case_id AND is_deleted = FALSE
            ORDER BY uploaded_at DESC
            LIMIT :limit OFFSET :offset
        """),
        {"case_id": case_id, "limit": limit, "offset": offset}
    )
    evidence_list = result.fetchall()
    
    total_result = await session.execute(
        text("SELECT COUNT(*) FROM evidence_files WHERE case_id = :case_id AND is_deleted = FALSE"),
        {"case_id": case_id}
    )
    total = total_result.scalar() or 0
    
    data = []
    for ev in evidence_list:
        data.append({
            "id": str(ev[0]),
            "filename": ev[1],
            "sha256_hash": ev[2][:16] + "..." if ev[2] else None,
            "file_size": ev[3],
            "mime_type": ev[4],
            "uploaded_by": str(ev[5]) if ev[5] else None,
            "uploaded_at": ev[6].isoformat() if ev[6] else None,
            "verified_at": ev[7].isoformat() if ev[7] else None,
            "integrity_status": ev[8]
        })
    
    return {
        "evidence": data,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{evidence_id}")
async def get_evidence_detail(
    evidence_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get detailed evidence information"""
    
    result = await session.execute(
        text("""
            SELECT id, filename, sha256_hash, file_size, mime_type,
                   storage_path, uploaded_by, uploaded_at, verified_at,
                   integrity_status, case_id
            FROM evidence_files
            WHERE id = :evidence_id AND is_deleted = FALSE
        """),
        {"evidence_id": evidence_id}
    )
    evidence = result.fetchone()
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence tidak ditemukan")
    
    return {
        "id": str(evidence[0]),
        "filename": evidence[1],
        "sha256_hash": evidence[2],
        "file_size": evidence[3],
        "mime_type": evidence[4],
        "storage_path": evidence[5],
        "uploaded_by": str(evidence[6]) if evidence[6] else None,
        "uploaded_at": evidence[7].isoformat() if evidence[7] else None,
        "verified_at": evidence[8].isoformat() if evidence[8] else None,
        "integrity_status": evidence[9],
        "case_id": str(evidence[10])
    }


@router.get("/case/{case_id}/custody")
async def get_custody_chain(
    case_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get custody chain for all evidence in a case"""
    
    result = await session.execute(
        text("""
            SELECT id, filename, sha256_hash, uploaded_at, uploaded_by,
                   integrity_status, verified_at
            FROM evidence_files
            WHERE case_id = :case_id AND is_deleted = FALSE
        """),
        {"case_id": case_id}
    )
    evidence_list = result.fetchall()
    
    custody_chains = []
    for ev in evidence_list:
        custody_chains.append({
            "evidence_id": str(ev[0]),
            "filename": ev[1],
            "sha256_hash": ev[2][:16] + "..." if ev[2] else None,
            "uploaded_at": ev[3].isoformat() if ev[3] else None,
            "uploaded_by": str(ev[4]) if ev[4] else None,
            "integrity_status": ev[5],
            "verified_at": ev[6].isoformat() if ev[6] else None
        })
    
    return {
        "case_id": case_id,
        "total_evidence": len(custody_chains),
        "custody_chains": custody_chains
    }


@router.get("/{evidence_id}/verify")
async def verify_evidence_integrity(
    evidence_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Verify evidence integrity by recalculating hash"""
    
    result = await session.execute(
        text("""
            SELECT storage_path, sha256_hash, filename
            FROM evidence_files
            WHERE id = :evidence_id
        """),
        {"evidence_id": evidence_id}
    )
    evidence = result.fetchone()
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence tidak ditemukan")
    
    try:
        with open(evidence[0], "rb") as f:
            content = f.read()
        computed_hash = hashlib.sha256(content).hexdigest()
        is_valid = computed_hash == evidence[1]
    except FileNotFoundError:
        is_valid = False
    
    status = "verified" if is_valid else "compromised"
    
    await session.execute(
        text("""
            UPDATE evidence_files 
            SET integrity_status = :status, verified_at = NOW()
            WHERE id = :evidence_id
        """),
        {"status": status, "evidence_id": evidence_id}
    )
    await session.commit()
    
    return {
        "evidence_id": evidence_id,
        "filename": evidence[2],
        "is_valid": is_valid,
        "integrity_status": status,
        "message": "Integritas bukti terverifikasi" if is_valid else "Integritas bukti GAGAL diverifikasi"
    }
