# scripts/metadata_inventory/diff_engine.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from .audit_result import AuditResult
from .dtos import Finding, FindingID, Severity, Evidence

@dataclass(frozen=True)
class DiffResult:
    """Hasil perbandingan antara dua snapshot."""
    added_tables: List[str] = field(default_factory=list)
    removed_tables: List[str] = field(default_factory=list)
    changed_tables: List[str] = field(default_factory=list)
    fingerprint_changed: bool = False
    findings: List[Finding] = field(default_factory=list)

class DiffEngine:
    """Diff engine untuk deteksi architectural drift."""
    
    def diff(self, baseline: AuditResult, current: AuditResult) -> DiffResult:
        """Bandingkan dua audit result."""
        added_tables = []
        removed_tables = []
        changed_tables = []
        
        # Get table fingerprints
        baseline_tables = self._get_table_fingerprints(baseline)
        current_tables = self._get_table_fingerprints(current)
        
        # Find differences
        for table_name, fingerprint in current_tables.items():
            if table_name not in baseline_tables:
                added_tables.append(table_name)
            elif baseline_tables[table_name] != fingerprint:
                changed_tables.append(table_name)
        
        for table_name in baseline_tables:
            if table_name not in current_tables:
                removed_tables.append(table_name)
        
        # Generate findings
        findings = []
        
        if added_tables:
            findings.append(Finding(
                id=FindingID.ORM200,
                severity=Severity.NOTICE,
                title="New tables detected",
                description=f"Added tables: {', '.join(added_tables)}",
                evidence=[Evidence(
                    description=f"Table '{t}' added",
                    source=f"diff_engine"
                ) for t in added_tables],
                recommendation="Ensure Alembic migration exists for new tables",
                affected_modules=[]  # Will be filled
            ))
        
        if removed_tables:
            findings.append(Finding(
                id=FindingID.ORM201,
                severity=Severity.WARNING,
                title="Tables removed",
                description=f"Removed tables: {', '.join(removed_tables)}",
                evidence=[Evidence(
                    description=f"Table '{t}' removed",
                    source=f"diff_engine"
                ) for t in removed_tables],
                recommendation="Ensure data migration is planned for removed tables",
                affected_modules=[]
            ))
        
        return DiffResult(
            added_tables=added_tables,
            removed_tables=removed_tables,
            changed_tables=changed_tables,
            fingerprint_changed=current.fingerprint != baseline.fingerprint,
            findings=findings
        )