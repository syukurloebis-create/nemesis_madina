"""Audit API Endpoints"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import UUID

from audit.services.report_generator import AuditReportGenerator
from audit.models import AuditReport, AuditReportRequest, ReportType, ReportFormat

router = APIRouter(prefix="/audit", tags=["audit"])


async def get_audit_generator():
    from backend.infrastructure.database import get_pool
    from investigation.services.case_service import InvestigationCaseService
    from investigation.repositories.case_repo import InvestigationCaseRepository, FindingRepository
    from backend.evidence.service import EvidenceService
    from backend.evidence.repository import EvidenceRepository
    from decision_trace.services.decision_trace_service import DecisionTraceService
    from decision_trace.repositories.decision_trace_repo import DecisionTraceRepository
    
    pool = await get_pool()
    case_repo = InvestigationCaseRepository(pool)
    finding_repo = FindingRepository(pool)
    evidence_repo = EvidenceRepository(pool)
    trace_repo = DecisionTraceRepository(pool)
    
    case_service = InvestigationCaseService(case_repo, finding_repo)
    evidence_service = EvidenceService(evidence_repo)
    trace_service = DecisionTraceService(trace_repo)
    
    return AuditReportGenerator(case_service, evidence_service, trace_service)


@router.post("/reports/generate", response_model=AuditReport)
async def generate_report(
    request: AuditReportRequest,
    generator: AuditReportGenerator = Depends(get_audit_generator)
):
    """Generate audit report for a case"""
    try:
        report = await generator.generate_report(request)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/reports/case/{case_id}")
async def get_case_reports(
    case_id: UUID,
    limit: int = 10,
    offset: int = 0
):
    """Get all reports for a case"""
    # Implementation would query database for existing reports
    return {"case_id": str(case_id), "reports": [], "total": 0}


@router.get("/templates")
async def get_report_templates():
    """Get available report templates"""
    return {
        "templates": [
            {
                "type": "lhp",
                "name": "Laporan Hasil Pemeriksaan",
                "description": "Full audit report for official use",
                "sections": ["Executive Summary", "Findings", "Evidence Matrix", "Recommendations", "Conclusion"]
            },
            {
                "type": "executive_summary",
                "name": "Executive Summary",
                "description": "High-level summary for management",
                "sections": ["Key Findings", "Risk Assessment", "Recommendations"]
            },
            {
                "type": "evidence_matrix",
                "name": "Evidence Matrix",
                "description": "Finding to evidence mapping",
                "sections": ["Finding", "Evidence", "Trace", "Confidence"]
            },
            {
                "type": "timeline",
                "name": "Audit Timeline",
                "description": "Chronological event timeline",
                "sections": ["Date", "Event", "Actor", "Evidence"]
            }
        ]
    }


@router.get("/formats")
async def get_supported_formats():
    """Get supported export formats"""
    return {
        "formats": [
            {"format": "json", "description": "JSON format for API consumption"},
            {"format": "pdf", "description": "PDF document for official use"},
            {"format": "docx", "description": "Word document for editing"},
            {"format": "html", "description": "HTML for web viewing"}
        ]
    }
