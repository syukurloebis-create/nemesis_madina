# scripts/metadata_inventory/contracts.py
"""
Contracts Module - Foundation of Verification Platform.
All contracts are immutable dataclasses.

L4 Enterprise Verification Platform - Phase 1
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Type, Set, Union
from enum import Enum
from datetime import datetime
import hashlib
import json


# ============================================================================
# CORE TYPES
# ============================================================================

@dataclass(frozen=True)
class ArtifactId:
    """Immutable artifact identifier."""
    value: str
    
    @classmethod
    def from_content(
        cls,
        name: str,
        payload: Dict[str, Any],
        producer: str,
        schema_version: str,
        parents: List['ArtifactId'] = None
    ) -> 'ArtifactId':
        from .canonical_serializer import CanonicalSerializer
        
        content = {
            "name": name,
            "payload": payload,
            "producer": producer,
            "schema_version": schema_version,
            "parents": [p.value for p in (parents or [])]
        }
        canonical = CanonicalSerializer.serialize(content)
        value = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        return cls(value)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ArtifactEnvelope:
    """Immutable artifact with full provenance."""
    artifact_id: ArtifactId
    name: str
    version: str
    schema_version: str
    producer: str
    produced_at: datetime
    payload: Dict[str, Any]
    checksum: str
    parents: List[ArtifactId] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        name: str,
        payload: Dict[str, Any],
        producer: str,
        schema_version: str = "1.0",
        parents: List[ArtifactId] = None,
        metadata: Dict[str, Any] = None
    ) -> 'ArtifactEnvelope':
        from .canonical_serializer import CanonicalSerializer
        from datetime import datetime
        
        artifact_id = ArtifactId.from_content(
            name=name,
            payload=payload,
            producer=producer,
            schema_version=schema_version,
            parents=parents
        )
        
        envelope_content = {
            "artifact_id": artifact_id.value,
            "name": name,
            "version": "1.0",
            "schema_version": schema_version,
            "producer": producer,
            "payload": payload,
            "parents": [p.value for p in (parents or [])],
            "metadata": metadata or {}
        }
        canonical = CanonicalSerializer.serialize(envelope_content)
        checksum = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        
        return cls(
            artifact_id=artifact_id,
            name=name,
            version="1.0",
            schema_version=schema_version,
            producer=producer,
            produced_at=datetime.now(),
            payload=payload,
            checksum=checksum,
            parents=parents or [],
            metadata=metadata or {}
        )
    
    def verify(self) -> bool:
        from .canonical_serializer import CanonicalSerializer
        import hashlib
        
        envelope_content = {
            "artifact_id": self.artifact_id.value,
            "name": self.name,
            "version": self.version,
            "schema_version": self.schema_version,
            "producer": self.producer,
            "payload": self.payload,
            "parents": [p.value for p in self.parents],
            "metadata": self.metadata
        }
        canonical = CanonicalSerializer.serialize(envelope_content)
        expected = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        return self.checksum == expected


@dataclass(frozen=True)
class ExecutionRecord:
    """Immutable record of a node execution."""
    node_name: str
    execution_id: str
    started_at: datetime
    completed_at: datetime
    status: str
    input_artifacts: List[ArtifactId]
    output_artifact: Optional[ArtifactId] = None
    error: Optional[str] = None
    retry_count: int = 0


# ============================================================================
# DEPENDENCY TYPES
# ============================================================================

class DependencyType(Enum):
    HARD = "hard"
    SOFT = "soft"
    OPTIONAL = "optional"


@dataclass(frozen=True)
class Dependency:
    """A dependency between nodes."""
    node_name: str
    dependency_type: DependencyType = DependencyType.HARD


# ============================================================================
# NODE DEFINITION
# ============================================================================

@dataclass(frozen=True)
class NodeDefinition:
    """Immutable node definition."""
    name: str
    engine: str
    depends_on: List[Dependency]
    input_types: Dict[str, type]
    output_type: type
    max_retries: int
    timeout_seconds: float
    retry_policy: str


# ============================================================================
# DISCOVERY ENGINE CONTRACTS
# ============================================================================

@dataclass(frozen=True)
class RegistryInfo:
    """Information about a SQLAlchemy registry."""
    metadata_id: int
    tables: List[str] = field(default_factory=list)
    models: List[str] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)
    mapper_count: int = 0
    is_canonical: bool = False
    is_active: bool = True


@dataclass(frozen=True)
class RegistryDiscoveryResult:
    """Result of registry discovery."""
    registries: Dict[int, RegistryInfo]
    canonical_metadata_id: Optional[int] = None
    total_registries: int = 0
    active_registries: int = 0


@dataclass(frozen=True)
class ModelInfo:
    """Information about an ORM model."""
    name: str
    module: str
    qualname: str
    is_abstract: bool = False
    is_mixin: bool = False
    has_tablename: bool = False


@dataclass(frozen=True)
class ModelDiscoveryResult:
    """Result of model discovery."""
    models: List[ModelInfo]
    total_models: int = 0
    concrete_models: int = 0
    abstract_models: int = 0


# ============================================================================
# RUNTIME ENGINE CONTRACTS
# ============================================================================

@dataclass(frozen=True)
class ImportResult:
    """Result of importing a module."""
    module: str
    success: bool
    mappers_before: int = 0
    mappers_after: int = 0
    mapper_identities_before: List[str] = field(default_factory=list)
    mapper_identities_after: List[str] = field(default_factory=list)
    grew: bool = False


@dataclass(frozen=True)
class RuntimeRegistrationResult:
    """Result of runtime registration audit."""
    module: str
    mappers: List[str] = field(default_factory=list)
    tables: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RuntimeResult:
    """Complete runtime audit result."""
    import_results: List[ImportResult]
    registration_results: List[RuntimeRegistrationResult]
    growth_results: List[Dict[str, Any]]


# ============================================================================
# ORM ENGINE CONTRACTS
# ============================================================================

@dataclass(frozen=True)
class MapperIntegrityResult:
    """Result of mapper integrity audit."""
    success: bool
    total_mappers: int
    invalid_mappers: List[Dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class MapperConfigResult:
    """Result of mapper configuration audit."""
    success: bool
    warnings: List[Dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class MetadataOwnershipResult:
    """Result of metadata ownership audit."""
    metadata_id: int
    tables: List[str] = field(default_factory=list)
    mappers: List[str] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)
    is_canonical: bool = False


@dataclass(frozen=True)
class RegistryConsistencyResult:
    """Result of registry consistency audit."""
    is_consistent: bool
    issues: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class CrossRegistryDependency:
    """A dependency between registries."""
    source_class: str
    source_module: str
    target_class: str
    target_module: str
    dependency_type: str


@dataclass(frozen=True)
class BootstrapCompletenessResult:
    """Result of bootstrap completeness audit."""
    expected_classes: List[str]
    actual_classes: List[str]
    missing_classes: List[str]
    completeness: float


@dataclass(frozen=True)
class MapperLifecycleResult:
    """Result of mapper lifecycle audit."""
    total_mappers: int
    configured: int
    unconfigured: int
    failed: int


@dataclass(frozen=True)
class ORMResult:
    """Complete ORM audit result."""
    integrity: Optional[MapperIntegrityResult] = None
    config: Optional[MapperConfigResult] = None
    ownership: List[MetadataOwnershipResult] = field(default_factory=list)
    consistency: Optional[RegistryConsistencyResult] = None
    cross_deps: List[CrossRegistryDependency] = field(default_factory=list)
    bootstrap: Optional[BootstrapCompletenessResult] = None
    lifecycle: Optional[MapperLifecycleResult] = None


# ============================================================================
# PERSISTENCE ENGINE CONTRACTS
# ============================================================================

@dataclass(frozen=True)
class PersistenceContractResult:
    """Result of persistence contract audit."""
    create_all_success: bool
    reflection_success: bool
    compare_success: bool
    errors: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class IdentityMapResult:
    """Result of identity map audit."""
    session_works: bool
    merge_works: bool
    expire_works: bool
    expunge_works: bool
    detached_works: bool


@dataclass(frozen=True)
class UnitOfWorkResult:
    """Result of unit of work audit."""
    flush_works: bool
    dirty_works: bool
    autoflush_works: bool
    rollback_works: bool


@dataclass(frozen=True)
class PersistenceResult:
    """Complete persistence audit result."""
    contract: Optional[PersistenceContractResult] = None
    identity_map: Optional[IdentityMapResult] = None
    unit_of_work: Optional[UnitOfWorkResult] = None


# ============================================================================
# DECISION CONTRACTS
# ============================================================================

class Severity(Enum):
    """Audit finding severity."""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class Evidence:
    """Evidence supporting a finding."""
    source: str
    artifact_id: str
    description: str
    details: Dict[str, Any]


@dataclass(frozen=True)
class Finding:
    """A finding from the audit."""
    type: str
    severity: Severity
    description: str
    evidence: List[Evidence]
    confidence: float = 1.0


@dataclass(frozen=True)
class DecisionResult:
    """Final decision result."""
    system_health: str
    deployment_decisions: Dict[str, str]
    findings: List[Finding]
    confidence: float = 1.0


# ============================================================================
# SELF-VALIDATION CONTRACTS
# ============================================================================

@dataclass(frozen=True)
class SelfValidationResult:
    """Result of self-validation."""
    name: str
    passed: bool
    message: str
    duration_seconds: float
    details: Optional[Dict[str, Any]] = None