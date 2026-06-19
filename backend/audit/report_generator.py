# backend/audit/report_generator.py
class AuditReportGenerator:
    async def generate_lhp(self, case_id: str) -> dict:
        """Generate Laporan Hasil Pemeriksaan"""
        case = await get_case(case_id)
        findings = await get_findings(case_id)
        evidence = await get_evidence_by_case(case_id)
        timeline = await get_timeline(case_id)
        
        return {
            "case_number": case.case_number,
            "title": case.title,
            "findings": [
                {
                    "finding": f.title,
                    "severity": f.severity,
                    "evidence_count": len(f.evidence_ids),
                    "recommendation": f.recommendation
                }
                for f in findings
            ],
            "evidence_matrix": [
                {"evidence_id": e.id, "hash": e.sha256_hash, "source": e.source_system}
                for e in evidence
            ],
            "timeline": timeline,
            "conclusion": self._generate_conclusion(findings)
        }