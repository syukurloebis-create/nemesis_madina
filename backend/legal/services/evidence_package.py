"""Legal Evidence Package Service - Court-ready evidence packaging"""

import hashlib
import json
import zipfile
from io import BytesIO
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID

from legal.models import (
    DigitalEvidencePackage, IntegrityCertificate, ChainOfCustodyRecord,
    LegalStatus, EvidenceFormat, ForensicExportRequest
)


class LegalEvidenceService:
    """Service for court-ready evidence packaging"""
    
    def __init__(self, case_service, evidence_service, trace_service):
        self.case_service = case_service
        self.evidence_service = evidence_service
        self.trace_service = trace_service
    
    async def create_evidence_package(
        self,
        case_id: UUID,
        evidence_ids: List[UUID],
        title: str,
        created_by: str
    ) -> DigitalEvidencePackage:
        """Create digital evidence package for court"""
        
        # Get all evidence
        evidences = []
        for evidence_id in evidence_ids:
            evidence = await self.evidence_service.get_evidence(evidence_id)
            if evidence:
                evidences.append(evidence)
        
        # Build hash chain
        hash_chain = []
        current_hash = "0"
        
        for evidence in evidences:
            computed = hashlib.sha256(
                f"{evidence.sha256_hash}{current_hash}".encode()
            ).hexdigest()
            hash_chain.append(computed)
            current_hash = computed
        
        # Compute Merkle root
        merkle_root = self._compute_merkle_root(hash_chain)
        
        # Create package
        package = DigitalEvidencePackage(
            case_id=case_id,
            package_number=f"EVP-{datetime.now().strftime('%Y%m%d')}-{len(hash_chain)}",
            title=title,
            evidence_ids=evidence_ids,
            trace_ids=[],  # Would add decision traces
            hash_chain=hash_chain,
            merkle_root=merkle_root,
            total_evidence=len(evidences),
            total_size_bytes=sum(e.file_size or 0 for e in evidences),
            legal_status=LegalStatus.DRAFT
        )
        
        return package
    
    async def certify_package(
        self,
        package_id: UUID,
        certifier: str,
        valid_days: int = 365
    ) -> IntegrityCertificate:
        """Certify evidence package with integrity certificate"""
        
        # Generate certificate
        certificate = IntegrityCertificate(
            package_id=package_id,
            certificate_number=f"CERT-{datetime.now().strftime('%Y%m%d')}-{package_id.hex[:8]}",
            issued_by=certifier,
            valid_until=datetime.now() + timedelta(days=valid_days),
            root_hash=hashlib.sha256(package_id.bytes).hexdigest(),
            signature=hashlib.sha256(f"{package_id}{certifier}{datetime.now().isoformat()}".encode()).hexdigest()
        )
        
        return certificate
    
    async def add_custody_record(
        self,
        evidence_id: UUID,
        action: str,
        actor: str,
        organization: str,
        purpose: str,
        hash_before: str,
        hash_after: str
    ) -> ChainOfCustodyRecord:
        """Add chain of custody record"""
        
        record = ChainOfCustodyRecord(
            evidence_id=evidence_id,
            action=action,
            actor=actor,
            organization=organization,
            purpose=purpose,
            hash_before=hash_before,
            hash_after=hash_after
        )
        
        return record
    
    async def export_forensic_package(
        self,
        request: ForensicExportRequest
    ) -> BytesIO:
        """Export forensic evidence package"""
        
        # Get case data
        case = await self.case_service.get_case(request.case_id)
        findings = await self.case_service.get_case_findings(request.case_id)
        
        # Create ZIP archive
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Export case JSON
            case_data = {
                "case_id": str(case.case_id),
                "case_number": case.case_number,
                "title": case.title,
                "status": case.status,
                "created_at": case.created_at.isoformat()
            }
            zip_file.writestr("case.json", json.dumps(case_data, indent=2, default=str))
            
            # Export findings
            findings_data = [
                {
                    "finding_id": str(f.finding_id),
                    "title": f.title,
                    "severity": f.severity,
                    "recommendation": f.recommendation
                }
                for f in findings
            ]
            zip_file.writestr("findings.json", json.dumps(findings_data, indent=2, default=str))
            
            # Export evidence if requested
            if request.include_evidence:
                for finding in findings:
                    for evidence_id in finding.evidence_ids:
                        evidence = await self.evidence_service.get_evidence(evidence_id)
                        if evidence:
                            zip_file.writestr(
                                f"evidence/{evidence.evidence_id}.json",
                                json.dumps(evidence.dict(), indent=2, default=str)
                            )
            
            # Add manifest
            manifest = {
                "exported_at": datetime.now().isoformat(),
                "format": request.format,
                "total_files": len(zip_file.namelist()),
                "integrity_hash": hashlib.sha256(str(zip_file.namelist()).encode()).hexdigest()
            }
            zip_file.writestr("MANIFEST.json", json.dumps(manifest, indent=2))
        
        zip_buffer.seek(0)
        return zip_buffer
    
    def _compute_merkle_root(self, hashes: List[str]) -> str:
        """Compute Merkle root from list of hashes"""
        if not hashes:
            return hashlib.sha256(b'empty').hexdigest()
        
        if len(hashes) == 1:
            return hashes[0]
        
        current_level = hashes.copy()
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = left + right
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            current_level = next_level
        
        return current_level[0]
