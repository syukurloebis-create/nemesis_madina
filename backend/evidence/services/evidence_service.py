"""Evidence Service - Business logic for evidence management"""

import hashlib
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from .models import (
    Evidence, EvidenceCreate, EvidenceVerification, CustodyRecord, CustodyAction,
    EvidenceStatus, SourceSystem, EvidenceType
)
from .repositories.evidence_repo import EvidenceRepository
from .repositories.custody_repo import CustodyRepository
from backend.core.hash.hasher import UnifiedHasher


class EvidenceService:
    """Service for evidence operations"""
    
    def __init__(self, evidence_repo: EvidenceRepository, custody_repo: CustodyRepository):
        self.evidence_repo = evidence_repo
        self.custody_repo = custody_repo
    
    async def upload_evidence(
        self,
        content: bytes,
        filename: str,
        source_system: SourceSystem,
        source_type: EvidenceType,
        uploaded_by: str,
        source_uri: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> Evidence:
        """Upload new evidence"""
        # Compute SHA256 hash
        sha256_hash = hashlib.sha256(content).hexdigest()
        
        # Create evidence record
        evidence = Evidence(
            sha256_hash=sha256_hash,
            filename=filename,
            mime_type=self._get_mime_type(filename),
            file_size=len(content),
            source_system=source_system,
            source_type=source_type,
            source_uri=source_uri,
            uploaded_by=uploaded_by,
            metadata=metadata or {},
            status=EvidenceStatus.PENDING
        )
        
        # Save to database
        evidence = await self.evidence_repo.create(evidence)
        
        # Add custody record
        custody = CustodyRecord(
            evidence_id=evidence.evidence_id,
            action=CustodyAction.UPLOADED,
            actor=uploaded_by,
            ip_address=ip_address,
            reason=f"Uploaded from {source_system.value}"
        )
        await self.custody_repo.add_record(custody)
        
        # In production, also save file to storage
        # await self.storage.save(evidence.evidence_id, content)
        
        return evidence
    
    async def verify_evidence(
        self,
        evidence_id: UUID,
        content: bytes,
        verified_by: str,
        ip_address: Optional[str] = None
    ) -> EvidenceVerification:
        """Verify evidence integrity"""
        evidence = await self.evidence_repo.get_by_id(evidence_id)
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")
        
        # Recompute hash
        computed_hash = hashlib.sha256(content).hexdigest()
        hash_match = computed_hash == evidence.sha256_hash
        
        # Update evidence
        if hash_match:
            await self.evidence_repo.mark_verified(evidence_id, verified_by, True)
        else:
            await self.evidence_repo.mark_verified(evidence_id, verified_by, False)
        
        # Add custody record
        custody = CustodyRecord(
            evidence_id=evidence_id,
            action=CustodyAction.VERIFIED,
            actor=verified_by,
            hash_before=evidence.sha256_hash,
            hash_after=computed_hash,
            ip_address=ip_address,
            reason="Integrity verification"
        )
        await self.custody_repo.add_record(custody)
        
        return EvidenceVerification(
            evidence_id=evidence_id,
            verified=hash_match,
            hash_match=hash_match,
            verified_at=datetime.now(),
            verified_by=verified_by,
            details={
                "stored_hash": evidence.sha256_hash[:16] + "...",
                "computed_hash": computed_hash[:16] + "..."
            }
        )
    
    async def get_evidence(self, evidence_id: UUID) -> Optional[Evidence]:
        """Get evidence by ID"""
        return await self.evidence_repo.get_by_id(evidence_id)
    
    async def get_custody_chain(self, evidence_id: UUID) -> List[CustodyRecord]:
        """Get full custody chain"""
        return await self.custody_repo.get_chain(evidence_id)
    
    async def link_to_decision(self, evidence_id: UUID, trace_id: str) -> bool:
        """Link evidence to decision trace"""
        # Implementation to link evidence to decision_trace
        # Update decision_trace.evidence_ids array
        pass
    
    async def list_evidence(
        self,
        limit: int = 100,
        offset: int = 0,
        source_system: Optional[str] = None
    ) -> List[Evidence]:
        """List evidence"""
        return await self.evidence_repo.list_evidence(limit, offset, source_system)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get evidence statistics"""
        return await self.evidence_repo.get_statistics()
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename"""
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        mime_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'json': 'application/json',
            'csv': 'text/csv'
        }
        return mime_types.get(ext, 'application/octet-stream')
