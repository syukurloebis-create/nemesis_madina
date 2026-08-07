# scripts/metadata_inventory/verification/rules.py
"""
Verification Rules - Individual verification rules.
"""

from typing import Dict, List, Optional, Any, Tuple, Type
from enum import Enum
from dataclasses import dataclass, field


class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class Evidence:
    """Evidence for a finding."""
    source: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Finding:
    """Immutable finding."""
    type: str
    severity: Severity
    description: str
    evidence: List[Evidence] = field(default_factory=list)
    affected_entities: List[str] = field(default_factory=list)


class VerificationRule:
    """Base class for verification rules."""
    
    def __init__(self, rule_id: str, version: str, severity: Severity, 
                 name: str, description: str, category: str):
        self._rule_id = rule_id
        self._version = version
        self._severity = severity
        self._name = name
        self._description = description
        self._category = category
    
    @property
    def rule_id(self) -> str:
        return self._rule_id
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def severity(self) -> Severity:
        return self._severity
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def category(self) -> str:
        return self._category
    
    def verify(self) -> List[Finding]:
        """Verify rule."""
        return []


class SingleCanonicalRegistryRule(VerificationRule):
    def __init__(self):
        super().__init__(
            rule_id="RULE-001@v1",
            version="1.0.0",
            severity=Severity.CRITICAL,
            name="Single Canonical Registry",
            description="Only one canonical registry should exist",
            category="registry"
        )


class AllModelsHaveTablesRule(VerificationRule):
    def __init__(self):
        super().__init__(
            rule_id="RULE-002@v1",
            version="1.0.0",
            severity=Severity.ERROR,
            name="All Models Have Tables",
            description="All models must have associated tables",
            category="model"
        )


class AllTablesHavePrimaryKeysRule(VerificationRule):
    def __init__(self):
        super().__init__(
            rule_id="RULE-003@v1",
            version="1.0.0",
            severity=Severity.ERROR,
            name="All Tables Have Primary Keys",
            description="All tables must have primary keys",
            category="table"
        )


class ImportSuccessRule(VerificationRule):
    def __init__(self):
        super().__init__(
            rule_id="RULE-004@v1",
            version="1.0.0",
            severity=Severity.CRITICAL,
            name="All Imports Successful",
            description="All imports must succeed",
            category="import"
        )
    
    def verify(self) -> List[Finding]:
        """Verify imports."""
        # Placeholder implementation
        return []


class ChecksumIntegrityRule(VerificationRule):
    def __init__(self):
        super().__init__(
            rule_id="RULE-005@v1",
            version="1.0.0",
            severity=Severity.CRITICAL,
            name="Checksum Integrity",
            description="Artifact checksum must match payload",
            category="integrity"
        )


class IdentityStabilityRule(VerificationRule):
    def __init__(self):
        super().__init__(
            rule_id="RULE-006@v1",
            version="1.0.0",
            severity=Severity.CRITICAL,
            name="Identity Stability",
            description="Artifact identity must be stable",
            category="identity"
        )


class DuplicateMapperRule(VerificationRule):
    def __init__(self):
        super().__init__(
            rule_id="RULE-007@v1",
            version="1.0.0",
            severity=Severity.WARNING,
            name="No Duplicate Mappers",
            description="No duplicate mappers should exist",
            category="mapper"
        )


class FKIntegrityRule(VerificationRule):
    def __init__(self):
        super().__init__(
            rule_id="RULE-008@v1",
            version="1.0.0",
            severity=Severity.ERROR,
            name="FK Integrity",
            description="Foreign keys must reference valid tables",
            category="integrity"
        )


# ============================================================================
# ALL_RULES - Registry of all rules
# ============================================================================

ALL_RULES = [
    SingleCanonicalRegistryRule(),
    AllModelsHaveTablesRule(),
    AllTablesHavePrimaryKeysRule(),
    ImportSuccessRule(),
    ChecksumIntegrityRule(),
    IdentityStabilityRule(),
    DuplicateMapperRule(),
    FKIntegrityRule(),
]


def get_all_rules() -> List[VerificationRule]:
    """Get all verification rules."""
    return ALL_RULES.copy()