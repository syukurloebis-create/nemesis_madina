# routers/evidence.py - Evidence endpoints (VERIFIED)
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.database import get_db
import json
import uuid
import hashlib
import aiofiles
import logging
from pathlib import Path
from typing import Optional
from collections import Counter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/evidence", tags=["evidence"])

# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

logger.info(f"📁 UPLOAD_DIR: {UPLOAD_DIR}")

def compute_confidence(score: float) -> str:
    if score >= 85:
        return "HIGH"
    elif score >= 70:
        return "MEDIUM"
    elif score >= 50:
        return "LOW"
    return "VERY_LOW"


# ============================================================
# UPLOAD EVIDENCE
# ============================================================

@router.post("/upload")
async def upload_evidence(
    file: UploadFile = File(...),
    case_id: str = Form(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    evidence_type: Optional[str] = Form("document"),
    db: AsyncSession = Depends(get_db)
):
    file_path = None

    try:
        evidence_id = str(uuid.uuid4())
        content = await file.read()
        file_size = len(content)
        sha256_hash = hashlib.sha256(content).hexdigest()
        content_type = file.content_type or "application/octet-stream"

        file_path = UPLOAD_DIR / f"{evidence_id}_{file.filename}"
        async with aiofiles.open(str(file_path), "wb") as f:
            await f.write(content)

        trust_score = 50.0
        if content_type in ["application/pdf", "image/png", "image/jpeg"]:
            trust_score = 70.0
        if content_type == "application/pdf":
            trust_score = 80.0

        confidence_level = compute_confidence(trust_score)

        scoring_detail = json.dumps({
            "file_type_score": trust_score,
            "hash_verified": False,
            "integrity_check": "pending"
        })

        query = """
        INSERT INTO evidence (
            id, case_id, filename, file_type, file_size,
            file_hash, trust_score, status, uploaded_at,
            updated_at, scoring_detail, confidence_level, storage_path
        )
        VALUES (
            :evidence_id, :case_id, :filename, :file_type, :file_size,
            :file_hash, :trust_score, 'UPLOADED', NOW(),
            NOW(), CAST(:scoring_detail AS jsonb),
            :confidence_level, :storage_path
        )
        """

        await db.execute(
            text(query),
            {
                "evidence_id": evidence_id,
                "case_id": case_id,
                "filename": file.filename,
                "file_type": content_type,
                "file_size": file_size,
                "file_hash": sha256_hash,
                "trust_score": trust_score,
                "scoring_detail": scoring_detail,
                "confidence_level": confidence_level,
                "storage_path": str(file_path)
            }
        )

        custody_query = """
        INSERT INTO custody_events (
            id, evidence_id, action, actor, timestamp, notes, metadata
        )
        VALUES (
            gen_random_uuid(), :evidence_id, 'UPLOAD', 'System',
            NOW(), 'Evidence uploaded to system', CAST(:metadata AS jsonb)
        )
        """

        metadata_json = json.dumps({
            "filename": file.filename,
            "file_type": content_type,
            "file_size": file_size,
            "sha256": sha256_hash,
            "uploaded_by": "system"
        })

        await db.execute(
            text(custody_query),
            {
                "evidence_id": evidence_id,
                "metadata": metadata_json
            }
        )

        await db.commit()

        return {
            "id": evidence_id,
            "filename": file.filename,
            "file_hash": sha256_hash,
            "trust_score": trust_score,
            "confidence_level": confidence_level,
            "status": "UPLOADED",
            "message": "Evidence uploaded successfully"
        }

    except Exception as e:
        await db.rollback()
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass
        logger.exception("Upload failed")
        raise HTTPException(500, str(e))


# ============================================================
# STATS
# ============================================================

@router.get("/stats")
async def get_evidence_stats(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("""
        SELECT
            COUNT(*) total,
            COUNT(*) FILTER(WHERE status='VERIFIED') verified,
            COUNT(*) FILTER(WHERE status='UPLOADED') pending,
            COUNT(*) FILTER(WHERE status='REJECTED') rejected
        FROM evidence
        """))
        row = result.fetchone()
        return {
            "total": row[0],
            "verified": row[1],
            "pending": row[2],
            "rejected": row[3]
        }
    except Exception as e:
        logger.exception("stats failed")
        raise HTTPException(500, str(e))


# ============================================================
# TOP
# ============================================================

@router.get("/top")
async def get_top_evidence(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            text("""
            SELECT id, case_id, filename, file_type,
                   trust_score, status, verified_at, uploaded_at
            FROM evidence
            ORDER BY trust_score DESC
            LIMIT :limit
            """),
            {"limit": limit}
        )
        rows = result.fetchall()
        return [
            {
                "id": str(r[0]),
                "case_id": str(r[1]),
                "filename": r[2],
                "file_type": r[3],
                "trust_score": float(r[4]),
                "status": r[5],
                "verified_at": r[6].isoformat() if r[6] else None,
                "uploaded_at": r[7].isoformat() if r[7] else None
            }
            for r in rows
        ]
    except Exception as e:
        logger.exception("top failed")
        raise HTTPException(500, str(e))


# ============================================================
# CHAIN
# ============================================================

@router.get("/{evidence_id}/chain")
async def get_evidence_chain(
    evidence_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        query = """
        SELECT id, case_id, filename, file_type, file_size,
               file_hash, trust_score, status, verified_at,
               uploaded_at, updated_at, scoring_detail,
               confidence_level, storage_path
        FROM evidence
        WHERE id = :evidence_id
        """
        result = await db.execute(text(query), {"evidence_id": evidence_id})
        ev_row = result.fetchone()

        if not ev_row:
            raise HTTPException(404, "Evidence not found")

        custody_query = """
        SELECT id, evidence_id, action, actor, timestamp, notes, metadata
        FROM custody_events
        WHERE evidence_id = :evidence_id
        ORDER BY timestamp ASC
        """
        custody_result = await db.execute(text(custody_query), {"evidence_id": evidence_id})
        custody_rows = custody_result.fetchall()

        custody_events = []
        for row in custody_rows:
            custody_events.append({
                "id": str(row[0]),
                "evidence_id": str(row[1]),
                "action": row[2],
                "actor": row[3],
                "timestamp": row[4].isoformat() if row[4] else None,
                "notes": row[5],
                "metadata": row[6] or {}
            })

        scoring_detail = ev_row[11] or {}
        hash_verified = scoring_detail.get("hash_verified", False)

        upload_exists = any(e["action"] == "UPLOAD" for e in custody_events)
        verify_exists = any(e["action"] == "VERIFY" for e in custody_events)

        storage_path = ev_row[13]
        storage_exists = bool(storage_path and Path(storage_path).exists())

        integrity = 0
        if upload_exists:
            integrity += 30
        if verify_exists:
            integrity += 30
        if hash_verified:
            integrity += 20
        if storage_exists:
            integrity += 20
        integrity = min(integrity, 100)

        is_verified_status = ev_row[7] == "VERIFIED"
        if is_verified_status and not verify_exists:
            integrity = min(integrity, 70)

        actions = Counter(e["action"] for e in custody_events)
        unique_actors = sorted({e["actor"] for e in custody_events if e["actor"]})

        return {
            "evidence": {
                "id": str(ev_row[0]),
                "case_id": str(ev_row[1]) if ev_row[1] else None,
                "filename": ev_row[2],
                "file_type": ev_row[3],
                "file_size": ev_row[4],
                "file_hash": ev_row[5],
                "trust_score": float(ev_row[6]) if ev_row[6] else 0,
                "status": ev_row[7],
                "verified_at": ev_row[8].isoformat() if ev_row[8] else None,
                "uploaded_at": ev_row[9].isoformat() if ev_row[9] else None,
                "updated_at": ev_row[10].isoformat() if ev_row[10] else None,
                "scoring_detail": scoring_detail,
                "confidence_level": ev_row[12],
                "storage_path": storage_path,
                "storage_available": storage_exists
            },
            "custody_events": custody_events,
            "summary": {
                "total_events": len(custody_events),
                "unique_actors": unique_actors,
                "actions": dict(actions),
                "chain_integrity": integrity,
                "hash_verified": hash_verified,
                "integrity_status": "STRONG" if integrity >= 85 else "MEDIUM" if integrity >= 60 else "WEAK",
                "consistency": "CONSISTENT" if not (is_verified_status and not verify_exists) else "INCONSISTENT"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting evidence chain")
        raise HTTPException(500, str(e))


# ============================================================
# VERIFY EVIDENCE
# ============================================================

@router.post("/{evidence_id}/verify")
async def verify_evidence(
    evidence_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        query = """
        SELECT id, file_hash, status, trust_score, confidence_level
        FROM evidence
        WHERE id = :evidence_id
        """
        result = await db.execute(text(query), {"evidence_id": evidence_id})
        row = result.mappings().fetchone()

        if not row:
            raise HTTPException(404, "Evidence not found")

        if row["status"] == "VERIFIED":
            return {
                "id": evidence_id,
                "status": row["status"],
                "trust_score": float(row["trust_score"] or 0),
                "confidence_level": row["confidence_level"],
                "verified": True,
                "message": "Evidence already verified"
            }

        files = list(UPLOAD_DIR.glob(f"{evidence_id}_*"))
        if not files:
            raise HTTPException(404, f"File not found in {UPLOAD_DIR}")

        file_path = files[0]
        async with aiofiles.open(str(file_path), "rb") as f:
            content = await f.read()

        current_hash = hashlib.sha256(content).hexdigest()
        is_verified = current_hash == row["file_hash"]

        previous_score = float(row["trust_score"] or 0)
        new_status = "VERIFIED" if is_verified else "REJECTED"
        new_trust = min(previous_score + 20, 100) if is_verified else max(previous_score - 30, 0)
        confidence = compute_confidence(new_trust)

        update_query = """
        UPDATE evidence
        SET status = :status,
            trust_score = :trust_score,
            confidence_level = :confidence,
            verified_at = NOW(),
            updated_at = NOW(),
            scoring_detail = jsonb_set(
                jsonb_set(
                    COALESCE(scoring_detail, '{}'::jsonb),
                    '{hash_verified}',
                    to_jsonb(CAST(:hash_verified AS boolean))
                ),
                '{integrity_check}',
                to_jsonb(CAST(:integrity_check AS text))
            )
        WHERE id = :evidence_id
        """

        await db.execute(
            text(update_query),
            {
                "status": new_status,
                "trust_score": new_trust,
                "confidence": confidence,
                "hash_verified": is_verified,
                "integrity_check": "passed" if is_verified else "failed",
                "evidence_id": evidence_id
            }
        )

        verify_metadata = {
            "verified_by": "AI",
            "hash_match": is_verified,
            "previous_hash": row["file_hash"],
            "current_hash": current_hash,
            "trust_score": new_trust,
            "confidence_level": confidence
        }

        custody_query = """
        INSERT INTO custody_events (
            id, evidence_id, action, actor, timestamp, notes, metadata
        )
        VALUES (
            gen_random_uuid(), :evidence_id, 'VERIFY', 'AI',
            NOW(), :notes, CAST(:metadata AS jsonb)
        )
        """

        await db.execute(
            text(custody_query),
            {
                "evidence_id": evidence_id,
                "notes": "Evidence verification successful" if is_verified else "Evidence verification failed",
                "metadata": json.dumps(verify_metadata)
            }
        )

        await db.commit()

        return {
            "id": evidence_id,
            "status": new_status,
            "trust_score": float(new_trust),
            "confidence_level": confidence,
            "verified": is_verified,
            "hash_verified": is_verified,
            "message": "Evidence verified" if is_verified else "Evidence rejected"
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("verify_evidence failed")
        raise HTTPException(500, str(e))


# ============================================================
# BY CASE
# ============================================================

@router.get("/case/{case_id}")
async def get_evidence_by_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            text("""
            SELECT id, filename, file_type, trust_score, status, uploaded_at
            FROM evidence
            WHERE case_id = :case_id
            ORDER BY uploaded_at DESC
            """),
            {"case_id": case_id}
        )
        rows = result.fetchall()
        return [
            {
                "id": str(r[0]),
                "filename": r[1],
                "file_type": r[2],
                "trust_score": float(r[3]),
                "status": r[4],
                "uploaded_at": r[5].isoformat() if r[5] else None
            }
            for r in rows
        ]
    except Exception as e:
        logger.exception("case evidence failed")
        raise HTTPException(500, str(e))