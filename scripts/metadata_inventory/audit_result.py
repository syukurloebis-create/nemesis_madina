# scripts/metadata_inventory/audit_result.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass(frozen=True)
class AuditResult:
    """
    AuditResult adalah passive immutable artifact.
    Tidak ada kalkulasi di sini.
    Semua nilai dihitung oleh pipeline dan dimasukkan sebagai field.
    """
    # Versioning
    audit_schema_version: str
    framework_version: str
    adr_version: str
    
    # Metadata
    metadata: List['MetadataDTO']
    relationships: List['RelationshipDTO']
    foreign_keys: List['ForeignKeyDTO']
    foreign_key_constraints: List['ForeignKeyConstraintDTO']
    
    # Analysis (sudah dihitung oleh pipeline)
    alembic_target: Optional['AlembicTargetDTO']
    bootstrap_stages: List['BootstrapStageDTO']
    
    # Findings & Scores (sudah dihitung)
    findings: List['Finding']
    health_score: Optional['HealthScore']
    classification: str
    
    # Summary (dihitung oleh builder, bukan oleh AuditResult)
    summary: 'AuditSummary'
    
    # Fingerprint
    fingerprint: str
    
    # Timestamp
    audit_timestamp: str

    recommendations: List['Recommendation'] = field(default_factory=list)

    fingerprint: Optional[Fingerprint] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialization dengan fingerprint version."""
        return {
            "audit_schema_version": self.audit_schema_version,
            "framework_version": self.framework_version,
            "contract_version": self.contract_version,
            "fingerprint": self.fingerprint.to_dict() if self.fingerprint else None,
            # ... rest of fields
        }

@dataclass(frozen=True)
class AuditSummary:
    """Summary yang dihitung oleh builder."""
    metadata_count: int
    table_count: int
    model_count: int
    cross_fk_count: int
    finding_count: int
    critical_count: int
    warning_count: int