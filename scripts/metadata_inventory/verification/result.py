# scripts/metadata_inventory/verification/result.py
"""
Verification Result - Immutable result artifact.
Phase 3 - ORM Verification Engine
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Type 

from .findings import Finding, FindingSummary


class VerificationStatus(Enum):
    PASSED = "PASSED"
    WARNING = "WARNING"
    FAILED = "FAILED"


@dataclass(frozen=True)
class VerificationMetadata:
    """Immutable metadata about the verification run."""
    engine_version: str
    rule_set_version: str
    discovery_version: str
    started_at: str
    finished_at: str
    duration_ms: int
    rules_executed: int


@dataclass(frozen=True)
class VerificationStatistics:
    """Statistics about verification run."""
    total_rules: int
    passed: int
    failed: int
    warning: int
    skipped: int
    info: int
    duration_ms: int
    rules_executed: int


@dataclass(frozen=True)
class VerificationResult:
    """
    Immutable verification result with full provenance.
    """
    artifact_fingerprint: str
    artifact_checksum: str
    status: VerificationStatus
    summary: FindingSummary
    findings: List[Finding]
    metadata: VerificationMetadata
    statistics: VerificationStatistics  # Must come BEFORE timestamp since it has no default
    timestamp: str
    payload_version: str = "1.0"  # Default values must come LAST
    verifier_version: str = "1.0"  # Default values must come LAST
    
    def to_payload(self) -> Dict[str, Any]:
        """Serialize to payload."""
        return {
            "payload_version": self.payload_version,
            "verifier_version": self.verifier_version,
            "timestamp": self.timestamp,
            "artifact_fingerprint": self.artifact_fingerprint,
            "artifact_checksum": self.artifact_checksum,
            "status": self.status.value,
            "summary": {
                "total": self.summary.total,
                "critical": self.summary.critical,
                "error": self.summary.error,
                "warning": self.summary.warning,
                "info": self.summary.info
            },
            "findings": [
                {
                    "type": f.type.value,
                    "severity": f.severity.value,
                    "description": f.description,
                    "evidence": [
                        {"source": e.source, "description": e.description, "details": e.details}
                        for e in f.evidence
                    ],
                    "recommendation": f.recommendation,
                    "affected_entities": f.affected_entities
                }
                for f in self.findings
            ],
            "metadata": {
                "engine_version": self.metadata.engine_version,
                "rule_set_version": self.metadata.rule_set_version,
                "discovery_version": self.metadata.discovery_version,
                "started_at": self.metadata.started_at,
                "finished_at": self.metadata.finished_at,
                "duration_ms": self.metadata.duration_ms,
                "rules_executed": self.metadata.rules_executed
            },
            "statistics": {
                "total_rules": self.statistics.total_rules,
                "passed": self.statistics.passed,
                "failed": self.statistics.failed,
                "warning": self.statistics.warning,
                "skipped": self.statistics.skipped,
                "info": self.statistics.info,
                "duration_ms": self.statistics.duration_ms,
                "rules_executed": self.statistics.rules_executed
            }
        }
    
    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> 'VerificationResult':
        """Reconstruct from payload."""
        from .findings import Finding, FindingSummary, Severity, FindingType, Evidence
        
        findings = []
        for f in payload.get("findings", []):
            findings.append(Finding(
                type=FindingType(f.get("type", "")),
                severity=Severity(f.get("severity", "INFO")),
                description=f.get("description", ""),
                evidence=[
                    Evidence(
                        source=e.get("source", ""),
                        description=e.get("description", ""),
                        details=e.get("details", {})
                    )
                    for e in f.get("evidence", [])
                ],
                recommendation=f.get("recommendation"),
                affected_entities=f.get("affected_entities", [])
            ))
        
        summary_data = payload.get("summary", {})
        summary = FindingSummary(
            total=summary_data.get("total", 0),
            critical=summary_data.get("critical", 0),
            error=summary_data.get("error", 0),
            warning=summary_data.get("warning", 0),
            info=summary_data.get("info", 0)
        )
        
        metadata_data = payload.get("metadata", {})
        metadata = VerificationMetadata(
            engine_version=metadata_data.get("engine_version", "1.0"),
            rule_set_version=metadata_data.get("rule_set_version", "1.0"),
            discovery_version=metadata_data.get("discovery_version", "1.0"),
            started_at=metadata_data.get("started_at", ""),
            finished_at=metadata_data.get("finished_at", ""),
            duration_ms=metadata_data.get("duration_ms", 0),
            rules_executed=metadata_data.get("rules_executed", 0)
        )
        
        stats_data = payload.get("statistics", {})
        statistics = VerificationStatistics(
            total_rules=stats_data.get("total_rules", 0),
            passed=stats_data.get("passed", 0),
            failed=stats_data.get("failed", 0),
            warning=stats_data.get("warning", 0),
            skipped=stats_data.get("skipped", 0),
            info=stats_data.get("info", 0),
            duration_ms=stats_data.get("duration_ms", 0),
            rules_executed=stats_data.get("rules_executed", 0)
        )
        
        return cls(
            artifact_fingerprint=payload.get("artifact_fingerprint", ""),
            artifact_checksum=payload.get("artifact_checksum", ""),
            status=VerificationStatus(payload.get("status", "PASSED")),
            summary=summary,
            findings=findings,
            metadata=metadata,
            statistics=statistics,
            timestamp=payload.get("timestamp", ""),
            payload_version=payload.get("payload_version", "1.0"),
            verifier_version=payload.get("verifier_version", "1.0")
        )
    
    def is_passed(self) -> bool:
        """Check if verification passed."""
        return self.status == VerificationStatus.PASSED
    
    def has_critical(self) -> bool:
        """Check if there are critical findings."""
        return self.summary.critical > 0
    
    def has_errors(self) -> bool:
        """Check if there are errors."""
        return self.summary.error > 0