"""Audit Report Generator - Generate professional audit reports"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

from audit.models import (
    AuditReport, AuditReportRequest, ReportType, ReportFormat,
    AuditFinding, EvidenceMatrix, AuditTimeline
)


class AuditReportGenerator:
    """Generate audit reports from case data"""
    
    def __init__(self, case_service, evidence_service, decision_trace_service):
        self.case_service = case_service
        self.evidence_service = evidence_service
        self.decision_trace_service = decision_trace_service
    
    async def generate_report(self, request: AuditReportRequest) -> AuditReport:
        """Generate audit report based on request"""
        
        # Get case data
        case = await self.case_service.get_case(request.case_id)
        if not case:
            raise ValueError(f"Case {request.case_id} not found")
        
        # Get findings
        findings = await self.case_service.get_case_findings(request.case_id)
        
        # Get evidence matrix
        evidence_matrix = await self._build_evidence_matrix(case, findings)
        
        # Build timeline
        timeline = await self._build_timeline(case, findings) if request.include_timeline else []
        
        # Generate content based on type
        content = self._generate_content(
            report_type=request.report_type,
            case=case,
            findings=findings,
            evidence_matrix=evidence_matrix,
            timeline=timeline
        )
        
        # Create report
        report = AuditReport(
            case_id=request.case_id,
            report_type=request.report_type,
            title=f"{request.report_type.value.upper()} - {case.case_number}",
            case_number=case.case_number,
            period_start=request.period_start or case.created_at,
            period_end=request.period_end or datetime.now(),
            findings=[self._to_audit_finding(f) for f in findings],
            evidence_matrix=evidence_matrix,
            timeline=timeline,
            conclusion=self._generate_conclusion(findings),
            recommendations=self._generate_recommendations(findings),
            generated_by="system",
            format=request.format,
            content=content
        )
        
        return report
    
    async def _build_evidence_matrix(self, case, findings) -> List[EvidenceMatrix]:
        """Build evidence to finding mapping matrix"""
        matrix = []
        
        for finding in findings:
            evidence_list = []
            trace_list = []
            
            for evidence_id in finding.evidence_ids:
                evidence = await self.evidence_service.get_evidence(evidence_id)
                if evidence:
                    evidence_list.append({
                        "id": str(evidence.evidence_id),
                        "filename": evidence.filename,
                        "hash": evidence.sha256_hash[:16],
                        "source": evidence.source_system,
                        "verified": evidence.is_verified
                    })
            
            for trace_id in finding.trace_ids:
                trace = await self.decision_trace_service.get_trace(trace_id)
                if trace:
                    trace_list.append({
                        "id": str(trace.trace_id),
                        "decision_type": trace.decision_type,
                        "score": trace.score,
                        "confidence": trace.confidence,
                        "reasons": trace.reasons
                    })
            
            matrix.append(EvidenceMatrix(
                finding_id=finding.finding_id,
                finding_title=finding.title,
                evidence_list=evidence_list,
                trace_list=trace_list,
                confidence_score=0.85  # Would calculate from evidence confidence
            ))
        
        return matrix
    
    async def _build_timeline(self, case, findings) -> List[AuditTimeline]:
        """Build audit timeline from case events"""
        timeline = []
        
        # Case creation
        timeline.append(AuditTimeline(
            timestamp=case.created_at,
            event_type="case_created",
            description=f"Case {case.case_number} created: {case.title}",
            metadata={"status": case.status, "priority": case.priority}
        ))
        
        # Case assignment
        if case.assigned_at:
            timeline.append(AuditTimeline(
                timestamp=case.assigned_at,
                event_type="case_assigned",
                description=f"Case assigned to {case.assigned_to}",
                actor=case.assigned_by
            ))
        
        # Finding creation
        for finding in findings:
            timeline.append(AuditTimeline(
                timestamp=finding.created_at,
                event_type="finding_created",
                description=f"Finding: {finding.title}",
                metadata={"severity": finding.severity}
            ))
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x.timestamp)
        
        return timeline
    
    def _generate_content(self, report_type: ReportType, case, findings, evidence_matrix, timeline) -> str:
        """Generate report content based on type"""
        
        if report_type == ReportType.EXECUTIVE_SUMMARY:
            return self._generate_executive_summary(case, findings)
        elif report_type == ReportType.EVIDENCE_MATRIX:
            return json.dumps([m.dict() for m in evidence_matrix], indent=2, default=str)
        elif report_type == ReportType.TIMELINE:
            return json.dumps([t.dict() for t in timeline], indent=2, default=str)
        else:
            return self._generate_full_report(case, findings, evidence_matrix, timeline)
    
    def _generate_executive_summary(self, case, findings) -> str:
        """Generate executive summary"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"EXECUTIVE SUMMARY")
        lines.append(f"Case: {case.case_number} - {case.title}")
        lines.append(f"Period: {case.created_at.strftime('%Y-%m-%d')} - {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("=" * 60)
        lines.append("")
        lines.append("KEY FINDINGS:")
        
        for i, finding in enumerate(findings[:5], 1):
            lines.append(f"  {i}. {finding.title} [{finding.severity.upper()}]")
            if finding.description:
                lines.append(f"     {finding.description[:100]}...")
        
        lines.append("")
        lines.append(f"Total Findings: {len(findings)}")
        lines.append(f"Critical: {sum(1 for f in findings if f.severity == 'critical')}")
        lines.append(f"High: {sum(1 for f in findings if f.severity == 'high')}")
        lines.append(f"Medium: {sum(1 for f in findings if f.severity == 'medium')}")
        lines.append(f"Low: {sum(1 for f in findings if f.severity == 'low')}")
        
        return "\n".join(lines)
    
    def _generate_full_report(self, case, findings, evidence_matrix, timeline) -> str:
        """Generate full audit report"""
        sections = []
        
        # Header
        sections.append("=" * 60)
        sections.append(f"AUDIT REPORT")
        sections.append(f"Case: {case.case_number} - {case.title}")
        sections.append(f"Generated: {datetime.now().isoformat()}")
        sections.append("=" * 60)
        
        # Executive Summary
        sections.append("\n## EXECUTIVE SUMMARY")
        sections.append(self._generate_executive_summary(case, findings))
        
        # Findings
        sections.append("\n## DETAILED FINDINGS")
        for i, finding in enumerate(findings, 1):
            sections.append(f"\n### Finding {i}: {finding.title}")
            sections.append(f"Severity: {finding.severity.upper()}")
            sections.append(f"Status: {finding.status}")
            if finding.description:
                sections.append(f"\nDescription: {finding.description}")
            if finding.recommendation:
                sections.append(f"\nRecommendation: {finding.recommendation}")
            sections.append(f"\nEvidence Count: {len(finding.evidence_ids)}")
            sections.append(f"Decision Traces: {len(finding.trace_ids)}")
        
        # Recommendations
        sections.append("\n## RECOMMENDATIONS")
        for i, rec in enumerate(self._generate_recommendations(findings), 1):
            sections.append(f"{i}. {rec}")
        
        # Conclusion
        sections.append("\n## CONCLUSION")
        sections.append(self._generate_conclusion(findings))
        
        return "\n".join(sections)
    
    def _generate_conclusion(self, findings) -> str:
        """Generate conclusion based on findings"""
        critical_count = sum(1 for f in findings if f.severity == "critical")
        high_count = sum(1 for f in findings if f.severity == "high")
        
        if critical_count > 0:
            return f"Based on {len(findings)} findings including {critical_count} critical issues, immediate action is required to address the identified risks and deficiencies."
        elif high_count > 0:
            return f"Based on {len(findings)} findings including {high_count} high-severity issues, management attention is recommended to address the identified concerns."
        else:
            return f"Based on {len(findings)} findings, overall risk level is moderate. Regular monitoring and follow-up are recommended."
    
    def _generate_recommendations(self, findings) -> List[str]:
        """Generate recommendations from findings"""
        recommendations = set()
        
        for finding in findings:
            if finding.recommendation:
                recommendations.add(finding.recommendation)
        
        # Add default recommendations if needed
        if not recommendations:
            recommendations.add("Implement corrective actions for identified findings")
            recommendations.add("Strengthen internal controls in high-risk areas")
            recommendations.add("Regular monitoring of vendor relationships")
        
        return list(recommendations)
    
    def _to_audit_finding(self, finding) -> AuditFinding:
        """Convert to AuditFinding model"""
        return AuditFinding(
            finding_id=finding.finding_id,
            title=finding.title,
            description=finding.description or "",
            severity=finding.severity,
            status=finding.status,
            evidence_ids=finding.evidence_ids,
            trace_ids=finding.trace_ids,
            recommendation=finding.recommendation,
            response=finding.response
        )
