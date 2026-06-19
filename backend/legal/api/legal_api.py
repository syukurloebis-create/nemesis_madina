"""Legal API - Court-ready evidence"""

from fastapi import APIRouter, HTTPException, Depends, Response
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from backend.legal.models import (
    DigitalEvidencePackage, IntegrityCertificate, ChainOfCustodyRecord,
    ForensicExportRequest, LegalStatus
)

router = APIRouter(prefix="/legal", tags=["legal"])


@router.post("/packages", response_model=DigitalEvidencePackage)
async def create_evidence_package(request: dict):
    """Create digital evidence package for court"""
    case_id = request.get("case_id")
    evidence_ids = request.get("evidence_ids", [])
    title = request.get("title", "Evidence Package")
    
    # Convert string UUID to UUID if needed
    if isinstance(case_id, str):
        case_id = UUID(case_id)
    if evidence_ids and isinstance(evidence_ids[0], str):
        evidence_ids = [UUID(eid) for eid in evidence_ids]
    
    package = DigitalEvidencePackage(
        case_id=case_id,
        package_number=f"EVP-{datetime.now().strftime('%Y%m%d')}-{len(evidence_ids)}",
        title=title,
        evidence_ids=evidence_ids,
        trace_ids=[],
        hash_chain=[],
        merkle_root="",
        total_evidence=len(evidence_ids),
        total_size_bytes=0
    )
    return package


@router.get("/packages/{package_id}", response_model=DigitalEvidencePackage)
async def get_evidence_package(package_id: UUID):
    """Get evidence package by ID"""
    raise HTTPException(status_code=404, detail="Package not found")


@router.post("/packages/{package_id}/certify", response_model=IntegrityCertificate)
async def certify_package(package_id: UUID, request: dict):
    """Certify evidence package with integrity certificate"""
    certifier = request.get("certifier", "system")
    return IntegrityCertificate(
        package_id=package_id,
        certificate_number=f"CERT-{datetime.now().strftime('%Y%m%d')}-{str(package_id)[:8]}",
        issued_by=certifier,
        valid_until=datetime.now(),
        root_hash="",
        signature=""
    )


@router.get("/packages/{package_id}/certificate", response_model=IntegrityCertificate)
async def get_certificate(package_id: UUID):
    """Get integrity certificate for package"""
    raise HTTPException(status_code=404, detail="Certificate not found")


@router.post("/custody")
async def add_custody_record(record: ChainOfCustodyRecord):
    """Add chain of custody record"""
    return record


@router.get("/custody/{evidence_id}")
async def get_custody_chain(evidence_id: UUID):
    """Get full custody chain for evidence"""
    return {"records": []}


@router.post("/export/forensic")
async def export_forensic_package(request: ForensicExportRequest):
    """Export forensic evidence package for court"""
    return {"message": "Export initiated", "format": request.format.value if hasattr(request.format, 'value') else request.format}


@router.get("/export/{package_id}/download")
async def download_forensic_package(package_id: UUID):
    """Download forensic evidence package"""
    return Response(content=b"", media_type="application/zip")


@router.get("/templates")
async def get_legal_templates():
    """Get legal document templates"""
    return {
        "templates": [
            {
                "id": "evidence_package",
                "name": "Digital Evidence Package",
                "description": "Complete package of digital evidence for court",
                "format": "zip",
                "includes": ["evidence", "hash_chain", "certificate", "manifest"]
            },
            {
                "id": "integrity_certificate",
                "name": "Integrity Certificate",
                "description": "Certificate of evidence integrity",
                "format": "pdf",
                "includes": ["hash", "timestamp", "signature"]
            },
            {
                "id": "chain_of_custody",
                "name": "Chain of Custody Report",
                "description": "Complete chain of custody documentation",
                "format": "pdf",
                "includes": ["timeline", "actors", "hash_changes"]
            },
            {
                "id": "forensic_export",
                "name": "Forensic Export Package",
                "description": "Court-ready forensic evidence export",
                "format": "zip",
                "includes": ["case_data", "findings", "evidence", "timeline", "graph"]
            }
        ]
    }
