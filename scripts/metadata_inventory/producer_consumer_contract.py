# producer_consumer_contract.py
"""
Producer-Consumer Contract Verification.
Phase 1.7 - Runtime Determinism & Contract Completeness
"""

from typing import Dict, List, Optional, Any, Callable, Type 
from dataclasses import dataclass, field
from enum import Enum

from contracts import ArtifactEnvelope, NodeDefinition


class ContractViolationSeverity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class ArtifactContract:
    """Contract for an artifact type."""
    name: str
    schema_version: str
    produced_by: str
    fields: Tuple[str, ...]  # Field names
    types: MappingProxyType  # field -> type name


@dataclass(frozen=True)
class ContractViolation:
    """A contract violation."""
    severity: ContractViolationSeverity
    message: str
    producer: Optional[str] = None
    consumer: Optional[str] = None
    artifact: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class ProducerConsumerContractVerifier:
    """
    Verifies producer-consumer contracts.
    """
    
    def __init__(self):
        self._contracts: Dict[str, ArtifactContract] = {}
    
    def register_contract(self, contract: ArtifactContract) -> None:
        """Register an artifact contract."""
        self._contracts[contract.name] = contract
    
    def verify_producer(
        self,
        node_name: str,
        output_type: Type,
        schema_version: str
    ) -> List[ContractViolation]:
        """Verify a producer node."""
        violations = []
        
        # Check if contract exists
        contract = self._contracts.get(output_type.__name__)
        if not contract:
            # Create implicit contract
            self.register_contract(ArtifactContract(
                name=output_type.__name__,
                schema_version=schema_version,
                produced_by=node_name,
                fields=tuple(),
                types=MappingProxyType({})
            ))
            return violations
        
        # Check schema version compatibility
        if contract.schema_version != schema_version:
            violations.append(ContractViolation(
                severity=ContractViolationSeverity.WARNING,
                message=f"Schema version mismatch: producer '{node_name}' uses {schema_version}, "
                        f"contract expects {contract.schema_version}",
                producer=node_name,
                artifact=output_type.__name__
            ))
        
        return violations
    
    def verify_consumer(
        self,
        node_name: str,
        artifact_name: str,
        expected_schema_version: str
    ) -> List[ContractViolation]:
        """Verify a consumer node."""
        violations = []
        
        contract = self._contracts.get(artifact_name)
        if not contract:
            violations.append(ContractViolation(
                severity=ContractViolationSeverity.ERROR,
                message=f"Unknown artifact '{artifact_name}' referenced by consumer '{node_name}'",
                consumer=node_name,
                artifact=artifact_name
            ))
            return violations
        
        # Check schema version compatibility
        if contract.schema_version != expected_schema_version:
            violations.append(ContractViolation(
                severity=ContractViolationSeverity.ERROR,
                message=f"Schema version mismatch: consumer '{node_name}' expects {expected_schema_version}, "
                        f"producer '{contract.produced_by}' uses {contract.schema_version}",
                consumer=node_name,
                producer=contract.produced_by,
                artifact=artifact_name
            ))
        
        return violations
    
    def verify_node_contracts(
        self,
        node_name: str,
        depends_on: List['Dependency'],
        output_type: Type,
        schema_version: str = "1.0"
    ) -> List[ContractViolation]:
        """Verify all contracts for a node."""
        violations = []
        
        # Verify as producer
        violations.extend(self.verify_producer(
            node_name=node_name,
            output_type=output_type,
            schema_version=schema_version
        ))
        
        # Verify as consumer (for each dependency)
        for dep in depends_on:
            violations.extend(self.verify_consumer(
                node_name=node_name,
                artifact_name=dep.node_name,
                expected_schema_version=schema_version
            ))
        
        return violations