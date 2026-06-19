"""Audit Models - Audit report generation and automation"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field


class ReportType(str, Enum):
    LHP = "lhp"  # Laporan Hasil Pemeriksaan
    NHP = "nhp"  # Nota Hasil Pemeriksaan
    EXECUTIVE_SUMMARY = "executive_summary"
    EVIDENCE_MATRIX = "evidence_matrix"
    TIMELINE = "timeline"
    CASE_DOSSIER = "case_dossier"


class ReportFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    JSON = "json"
    HTML = "html"


class AuditFinding(BaseModel):
    """Audit finding structure"""
    finding_id: UUID
    title: str
    description: str
    severity: str
    status: str
    evidence_ids: List[UUID]
    trace_ids: List[UUID]
    recommendation: Optional[str] = None
    response: Optional[str] = None


class EvidenceMatrix(BaseModel):
    """Evidence to finding mapping matrix"""
    finding_id: UUID
    finding_title: str
    evidence_list: List[Dict[str, Any]]
    trace_list: List[Dict[str, Any]]
    confidence_score: float


class AuditTimeline(BaseModel):
    """Audit timeline event"""
    timestamp: datetime
    event_type: str
    description: str
    actor: Optional[str] = None
    evidence_id: Optional[UUID] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AuditReport(BaseModel):
    """Complete audit report"""
    report_id: UUID = Field(default_factory=uuid4)
    case_id: UUID
    report_type: ReportType
    title: str
    case_number: str
    period_start: datetime
    period_end: datetime
    findings: List[AuditFinding]
    evidence_matrix: List[EvidenceMatrix]
    timeline: List[AuditTimeline]
    conclusion: str
    recommendations: List[str]
    generated_by: str
    generated_at: datetime = Field(default_factory=datetime.now)
    format: ReportFormat = ReportFormat.JSON
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AuditReportRequest(BaseModel):
    """Request to generate audit report"""
    case_id: UUID
    report_type: ReportType
    format: ReportFormat = ReportFormat.JSON
    include_evidence: bool = True
    include_timeline: bool = True
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
