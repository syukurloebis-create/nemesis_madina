# services/auto_verifier.py - Auto Verification Pipeline (FIXED)
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

class AutoVerifier:
    """Auto verification pipeline for evidence"""
    
    @staticmethod
    async def verify_evidence(
        evidence_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Auto verify evidence with proper transaction
        
        ============ FIX: Pastikan commit terjadi ============
        """
        try:
            # 1. Get evidence data
            result = await db.execute(text("""
                SELECT 
                    id, filename, file_hash, file_size,
                    file_type, trust_score, status,
                    storage_path
                FROM evidence 
                WHERE id = :id
            """), {"id": evidence_id})
            row = result.fetchone()
            
            if not row:
                return {"status": "failed", "reason": "Evidence not found"}
            
            evidence_data = {
                "id": row[0],
                "filename": row[1],
                "file_hash": row[2],
                "file_size": row[3],
                "file_type": row[4],
                "trust_score": row[5] or 0,
                "status": row[6],
                "storage_path": row[7]
            }
            
            # 2. Run checks
            hash_valid = bool(evidence_data["file_hash"] and len(evidence_data["file_hash"]) == 64)
            type_valid = evidence_data["file_type"] in [
                "application/pdf", "image/png", "image/jpeg", 
                "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ]
            size_valid = evidence_data["file_size"] > 100
            
            # 3. Calculate score
            score = 0
            if hash_valid:
                score += 30
            if type_valid:
                score += 30
            if size_valid:
                score += 20
            if evidence_data["file_type"] and evidence_data["file_type"].startswith("image"):
                score += 20
            
            is_verified = score >= 70
            
            # 4. Update database with proper transaction
            if is_verified:
                from services.evidence_scoring import EvidenceScorer
                confidence = EvidenceScorer.calculate_confidence(
                    trust_score=score,
                    status="verified"
                )
                
                # ============ FIX: Pastikan commit ============
                await db.execute(text("""
                    UPDATE evidence 
                    SET status = 'verified',
                        verified_at = NOW(),
                        trust_score = :score,
                        confidence_level = :confidence
                    WHERE id = :id
                """), {"id": evidence_id, "score": score, "confidence": confidence})
                
                # ============ FIX: Explicit commit ============
                await db.commit()
                
                # ============ FIX: Refresh data ============
                refresh_result = await db.execute(text("""
                    SELECT status, trust_score, confidence_level, verified_at
                    FROM evidence 
                    WHERE id = :id
                """), {"id": evidence_id})
                refreshed = refresh_result.fetchone()
                
                return {
                    "status": "verified",
                    "score": score,
                    "confidence": confidence,
                    "verified_at": refreshed[3].isoformat() if refreshed[3] else None,
                    "message": "Auto verification completed"
                }
            else:
                return {
                    "status": "pending",
                    "score": score,
                    "checks": {
                        "hash_valid": hash_valid,
                        "type_valid": type_valid,
                        "size_valid": size_valid
                    },
                    "message": "Evidence did not meet verification criteria"
                }
                
        except Exception as e:
            logger.error(f"Auto verification error: {str(e)}")
            await db.rollback()
            return {"status": "failed", "reason": str(e)}
