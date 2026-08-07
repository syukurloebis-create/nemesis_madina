# contract_verifier.py
"""
Contract Verifier - Validates producer/consumer contracts.
Phase 1.6 - Contract Enforcement & Abstraction
"""

from typing import Dict, List, Optional, Any, Callable, Type 
from dataclasses import dataclass, field

from contracts import ArtifactEnvelope, NodeDefinition, Dependency, DependencyType
from artifact_identity import ArtifactIdentity


@dataclass(frozen=True)
class ContractViolation:
    """A contract violation."""
    severity: str  # ERROR, WARNING
    message: str
    node: Optional[str] = None
    artifact: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class ContractVerifier:
    """
    Verifies producer/consumer contracts at registration time.
    """
    
    def __init__(self):
        self._violations: List[ContractViolation] = []
    
    def verify_node(
        self,
        node_name: str,
        depends_on: List[Dependency],
        input_types: Dict[str, Type],
        output_type: Type,
        runner: Any
    ) -> List[ContractViolation]:
        """Verify a node's contracts."""
        violations = []
        
        # Check input types
        for dep in depends_on:
            if dep.node_name not in input_types and dep.dependency_type == DependencyType.HARD:
                violations.append(ContractViolation(
                    severity="ERROR",
                    message=f"Node '{node_name}' has hard dependency on '{dep.node_name}' but no input type specified",
                    node=node_name,
                    artifact=dep.node_name
                ))
        
        # Check output type
        if output_type is None:
            violations.append(ContractViolation(
                severity="ERROR",
                message=f"Node '{node_name}' has no output type specified",
                node=node_name
            ))
        
        # Check runner returns correct type
        if runner:
            import inspect
            if not callable(runner):
                violations.append(ContractViolation(
                    severity="ERROR",
                    message=f"Runner for '{node_name}' is not callable",
                    node=node_name
                ))
        
        return violations
    
    def verify_artifact_compatibility(
        self,
        producer: str,
        artifact: ArtifactEnvelope,
        consumer: str,
        expected_schema_version: str
    ) -> List[ContractViolation]:
        """Verify artifact compatibility between producer and consumer."""
        violations = []
        
        # Check schema version
        if artifact.schema_version != expected_schema_version:
            violations.append(ContractViolation(
                severity="WARNING",
                message=f"Schema version mismatch: producer '{producer}' uses {artifact.schema_version}, "
                        f"consumer '{consumer}' expects {expected_schema_version}",
                artifact=artifact.name,
                details={
                    "producer": producer,
                    "consumer": consumer,
                    "producer_version": artifact.schema_version,
                    "consumer_version": expected_schema_version
                }
            ))
        
        # Check producer matches
        if artifact.producer != producer:
            violations.append(ContractViolation(
                severity="ERROR",
                message=f"Artifact produced by '{artifact.producer}' but claimed by '{producer}'",
                artifact=artifact.name
            ))
        
        return violations
    
    def verify_dag_contracts(self, nodes: Dict[str, NodeDefinition]) -> List[ContractViolation]:
        """Verify all contracts in a DAG."""
        violations = []
        
        for name, node in nodes.items():
            # Check each dependency
            for dep in node.depends_on:
                if dep.node_name not in nodes:
                    violations.append(ContractViolation(
                        severity="ERROR",
                        message=f"Node '{name}' depends on unknown node '{dep.node_name}'",
                        node=name
                    ))
            
            # Check input types
            for dep in node.depends_on:
                if dep.node_name in nodes and dep.node_name not in node.input_types:
                    if dep.dependency_type == DependencyType.HARD:
                        violations.append(ContractViolation(
                            severity="ERROR",
                            message=f"Node '{name}' has hard dependency on '{dep.node_name}' but no input type",
                            node=name
                        ))
            
            # Check optional dependency consistency
            for dep in node.depends_on:
                if dep.dependency_type == DependencyType.OPTIONAL:
                    if dep.node_name not in node.input_types:
                        violations.append(ContractViolation(
                            severity="WARNING",
                            message=f"Node '{name}' has optional dependency on '{dep.node_name}' but no input type",
                            node=name
                        ))
        
        return violations
    
    def verify_all(
        self,
        nodes: Dict[str, NodeDefinition],
        runners: Dict[str, Any]
    ) -> Dict[str, List[ContractViolation]]:
        """Verify all contracts."""
        all_violations = {}
        
        # Verify DAG contracts
        dag_violations = self.verify_dag_contracts(nodes)
        if dag_violations:
            all_violations["dag"] = dag_violations
        
        # Verify each node
        for name, node in nodes.items():
            runner = runners.get(name)
            violations = self.verify_node(
                node_name=name,
                depends_on=node.depends_on,
                input_types=node.input_types,
                output_type=node.output_type,
                runner=runner
            )
            if violations:
                all_violations[name] = violations
        
        return all_violations