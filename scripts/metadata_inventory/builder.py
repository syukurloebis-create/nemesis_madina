# scripts/metadata_inventory/builder.py
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from .audit_result import AuditResult, AuditSummary
from .dtos import (
    MetadataDTO, RelationshipDTO, ForeignKeyDTO, 
    ForeignKeyConstraintDTO, AlembicTargetDTO, 
    BootstrapStageDTO, Finding, HealthScore
)

class AuditResultBuilder:
    """
    SATU-SATUNYA factory untuk AuditResult.
    Tidak boleh ada kode lain yang menginstansiasi AuditResult secara langsung.
    """
    
    def __init__(self):
        self._metadata: List[MetadataDTO] = []
        self._relationships: List[RelationshipDTO] = []
        self._foreign_keys: List[ForeignKeyDTO] = []
        self._foreign_key_constraints: List[ForeignKeyConstraintDTO] = []
        self._alembic_target: Optional[AlembicTargetDTO] = None
        self._bootstrap_stages: List[BootstrapStageDTO] = []
        self._findings: List[Finding] = []
        self._health_score: Optional[HealthScore] = None
        self._classification: str = "UNKNOWN"
        self._fingerprint: str = ""
    
    def with_metadata(self, metadata: List[MetadataDTO]) -> 'AuditResultBuilder':
        self._metadata = metadata
        return self
    
    def with_relationships(self, relationships: List[RelationshipDTO]) -> 'AuditResultBuilder':
        self._relationships = relationships
        return self
    
    def with_foreign_keys(self, fks: List[ForeignKeyDTO]) -> 'AuditResultBuilder':
        self._foreign_keys = fks
        return self
    
    def with_findings(self, findings: List[Finding]) -> 'AuditResultBuilder':
        self._findings = findings
        return self
    
    def with_health_score(self, score: HealthScore) -> 'AuditResultBuilder':
        self._health_score = score
        return self
    
    def build(self) -> AuditResult:
        """Build AuditResult. Satu-satunya tempat instansiasi AuditResult."""
        summary = AuditSummary(
            metadata_count=len(self._metadata),
            table_count=sum(len(m.table_names) for m in self._metadata),
            model_count=sum(len(m.model_names) for m in self._metadata),
            cross_fk_count=len(self._foreign_keys),
            finding_count=len(self._findings),
            critical_count=sum(1 for f in self._findings if f.severity.value == "CRITICAL"),
            warning_count=sum(1 for f in self._findings if f.severity.value == "WARNING")
        )
        
        return AuditResult(
            audit_schema_version="1.0",
            framework_version="1.0.0",
            adr_version="ADR-034",
            metadata=self._metadata,
            relationships=self._relationships,
            foreign_keys=self._foreign_keys,
            foreign_key_constraints=self._foreign_key_constraints,
            alembic_target=self._alembic_target,
            bootstrap_stages=self._bootstrap_stages,
            findings=self._findings,
            health_score=self._health_score,
            classification=self._classification,
            summary=summary,
            fingerprint=self._fingerprint,
            audit_timestamp=datetime.now().isoformat()
        )