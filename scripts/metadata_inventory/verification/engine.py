# scripts/metadata_inventory/verification/engine.py
"""
Verification Engine - Orchestrates verification stages.
Phase 3 - ORM Verification Engine
"""

from typing import Dict, List, Optional, Any, Type 
from dataclasses import dataclass, field

from .findings import Finding, FindingSummary, Severity
from .result import VerificationResult
from .rules import VerificationRule, RuleContext
from .rules import ALL_RULES  


def __init__(self, rules: List[VerificationRule] = None):
        self.rules = rules or ALL_RULES
        self.rules = RuleRegistry.all()
        self.dependency_graph = RuleDependencyGraph
    
    def verify(self, artifact: Any, registry: Optional[Any] = None) -> VerificationResult:
        started_at = datetime.now()
        
        # 1. Identity verification (independent)
        identity_findings = self._verify_identity(artifact)
        
        # 2. Integrity verification (independent)
        integrity_findings = self._verify_integrity(artifact)
        
        # 3. Semantic verification with dependency graph
        semantic_findings = self._verify_semantic_with_deps(artifact, registry)
        
        # 4. All findings
        all_findings = identity_findings + integrity_findings + semantic_findings
        
        finished_at = datetime.now()
        duration_ms = int((finished_at - started_at).total_seconds() * 1000)
        
        # 5. Build result with provenance
        metadata = VerificationMetadata(
            engine_version="1.0.0",
            rule_set_version="2026.08",
            discovery_version=artifact.payload_version if artifact else "unknown",
            started_at=started_at.isoformat(),
            finished_at=finished_at.isoformat(),
            duration_ms=duration_ms,
            rules_executed=len(self.rules)
        )
        
        return self._build_result(artifact, all_findings, metadata)
    
    def _verify_semantic_with_deps(self, artifact, registry) -> List[Finding]:
        findings = []
        failed_rules = set()
        order = RuleDependencyGraph.get_order()
        
        for rule_id in order:
            rule = RuleRegistry.get(rule_id)
            if not rule:
                continue
            
            # Check if rule should be skipped
            if RuleDependencyGraph.can_skip(rule_id, failed_rules):
                findings.append(Finding(
                    type=FindingType.RULE_SKIPPED,
                    severity=Severity.INFO,
                    description=f"Rule '{rule_id}' skipped due to failed dependency",
                    evidence=[],
                    affected_entities=[],
                    status=FindingStatus.SKIPPED
                ))
                continue
            
            # Apply rule
            context = RuleContext(artifact=artifact, registry=registry)
            try:
                rule_findings = rule.verify(context)
                findings.extend(rule_findings)
                
                # Track failed rules
                for f in rule_findings:
                    if f.status == FindingStatus.FAIL:
                        failed_rules.add(rule_id)
                        break
            except Exception as e:
                findings.append(Finding(
                    type=FindingType.RULE_EXECUTION_ERROR,
                    severity=Severity.CRITICAL,
                    description=f"Rule '{rule_id}' execution failed: {e}",
                    evidence=[],
                    affected_entities=[],
                    status=FindingStatus.FAIL
                ))
                failed_rules.add(rule_id)
        
        return findings
    
    def _verify_identity(self, artifact: Any) -> List[Finding]:
        """Stage 1: Verify artifact identity."""
        from .rules import IdentityStabilityRule
        rule = IdentityStabilityRule()
        context = RuleContext(artifact=artifact)
        return rule.apply(context)
    
    def _verify_integrity(self, artifact: Any) -> List[Finding]:
        """Stage 2: Verify artifact integrity."""
        from .rules import ChecksumIntegrityRule
        rule = ChecksumIntegrityRule()
        context = RuleContext(artifact=artifact)
        return rule.apply(context)
    
    def _verify_semantic(self, artifact: Any, registry: Optional[Any]) -> List[Finding]:
        """Stage 3: Verify semantic content."""
        findings = []
        
        # Prepare context
        context = RuleContext(
            artifact=artifact,
            registry=registry,
            import_artifact=artifact.import_artifact if artifact else None,
            registry_artifact=artifact.registry_artifact if artifact else None
        )
        
        # Apply all semantic rules
        for rule in self.rules:
            # Skip identity/integrity rules (already handled)
            if rule.name in ["identity_stability", "checksum_integrity"]:
                continue
            try:
                rule_findings = rule.apply(context)
                findings.extend(rule_findings)
            except Exception as e:
                # Capture rule execution errors
                findings.append(Finding(
                    type=FindingType.RULE_EXECUTION_ERROR,
                    severity=Severity.CRITICAL,
                    description=f"Rule '{rule.name}' execution failed: {e}",
                    evidence=[],
                    recommendation="Check rule implementation"
                ))
        
        return findings
    
    def _build_result(self, artifact: Any, findings: List[Finding]) -> 'VerificationResult':
        """Build immutable VerificationResult."""
        from .result import VerificationResult, VerificationStatus
        
        # Count by severity
        critical = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        error = sum(1 for f in findings if f.severity == Severity.ERROR)
        warning = sum(1 for f in findings if f.severity == Severity.WARNING)
        info = sum(1 for f in findings if f.severity == Severity.INFO)
        
        summary = FindingSummary(
            total=len(findings),
            critical=critical,
            error=error,
            warning=warning,
            info=info
        )
        
        # Determine status
        if critical > 0:
            status = VerificationStatus.FAILED
        elif error > 0:
            status = VerificationStatus.FAILED
        elif warning > 0:
            status = VerificationStatus.WARNING
        else:
            status = VerificationStatus.PASSED
        
        return VerificationResult(
            artifact_fingerprint=artifact.fingerprint if artifact else "",
            artifact_checksum=artifact.checksum if artifact else "",
            status=status,
            summary=summary,
            findings=findings,
            timestamp=artifact.timestamp if artifact else "",
            payload_version=artifact.payload_version if artifact else "1.0"
        )