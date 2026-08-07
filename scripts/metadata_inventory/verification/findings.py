# scripts/metadata_inventory/verification/findings.py
"""
Finding Models - Immutable findings from verification.
Phase 3 - ORM Verification Engine
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Type 


class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class FindingType(Enum):
    # Registry findings
    MULTIPLE_REGISTRIES = "multiple_registries"
    CANONICAL_REGISTRY_MISSING = "canonical_registry_missing"
    REGISTRY_FINGERPRINT_MISMATCH = "registry_fingerprint_mismatch"
    
    # Mapper findings
    MAPPER_MISSING = "mapper_missing"
    MAPPER_DUPLICATE = "mapper_duplicate"
    MAPPER_NO_TABLE = "mapper_no_table"
    MAPPER_NO_PRIMARY_KEY = "mapper_no_primary_key"
    
    # Table findings
    TABLE_MISSING = "table_missing"
    TABLE_EXTRA = "table_extra"
    TABLE_SCHEMA_MISMATCH = "table_schema_mismatch"
    
    # Relationship findings
    FK_TABLE_MISSING = "fk_table_missing"
    FK_COLUMN_MISSING = "fk_column_missing"
    FK_CYCLE = "fk_cycle"
    
    # Import findings
    IMPORT_FAILED = "import_failed"
    IMPORT_NO_GROWTH = "import_no_growth"
    
    # Integrity findings
    CHECKSUM_MISMATCH = "checksum_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"


@dataclass(frozen=True)
class Evidence:
    """Evidence for a finding."""
    source: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Finding:
    """Immutable finding from verification."""
    type: FindingType
    severity: Severity
    description: str
    evidence: List[Evidence]
    recommendation: Optional[str] = None
    affected_entities: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class FindingSummary:
    """Summary of findings by severity."""
    total: int
    critical: int
    error: int
    warning: int
    info: int