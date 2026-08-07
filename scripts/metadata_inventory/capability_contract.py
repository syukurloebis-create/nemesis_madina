# capability_contract.py
"""
Capability Contract - Declarative runtime requirements.
Phase 1.7 - Runtime Determinism & Contract Completeness
"""

from typing import Dict, List, Optional, Any, Callable, Type, FrozenSet
from dataclasses import dataclass, field
from enum import Enum


class CapabilityType(Enum):
    SQLALCHEMY = "sqlalchemy"
    ALEMBIC = "alembic"
    POSTGRES = "postgres"
    REDIS = "redis"
    NETWORK = "network"
    GPU = "gpu"
    ASYNC = "async"
    TRANSACTIONAL = "transactional"
    DATABASE = "database"
    EVENT_STORE = "event_store"


@dataclass(frozen=True)
class CapabilityRequirement:
    """A capability requirement for a node."""
    capability: CapabilityType
    version: Optional[str] = None
    required: bool = True
    description: Optional[str] = None


@dataclass(frozen=True)
class CapabilityContract:
    """
    Capability contract for a node.
    Declares what capabilities the node requires.
    """
    node_name: str
    requirements: FrozenSet[CapabilityRequirement]
    
    def requires(self, capability: CapabilityType) -> bool:
        """Check if capability is required."""
        return any(r.capability == capability and r.required for r in self.requirements)
    
    def can_run_on(self, available: Set[CapabilityType]) -> bool:
        """Check if node can run with available capabilities."""
        for req in self.requirements:
            if req.required and req.capability not in available:
                return False
        return True


class CapabilityContractVerifier:
    """
    Verifies capability contracts.
    """
    
    def __init__(self):
        self._contracts: Dict[str, CapabilityContract] = {}
        self._available: Set[CapabilityType] = set()
    
    def register_node_capabilities(
        self,
        node_name: str,
        requirements: List[CapabilityRequirement]
    ) -> None:
        """Register capability requirements for a node."""
        self._contracts[node_name] = CapabilityContract(
            node_name=node_name,
            requirements=frozenset(requirements)
        )
    
    def set_available_capabilities(self, capabilities: Set[CapabilityType]) -> None:
        """Set available capabilities in the environment."""
        self._available = capabilities
    
    def verify_node(self, node_name: str) -> List[str]:
        """Verify node can run with available capabilities."""
        errors = []
        
        contract = self._contracts.get(node_name)
        if not contract:
            return errors
        
        for req in contract.requirements:
            if req.required and req.capability not in self._available:
                errors.append(
                    f"Node '{node_name}' requires {req.capability.value}{f' {req.version}' if req.version else ''}"
                )
        
        return errors
    
    def verify_all(self) -> Dict[str, List[str]]:
        """Verify all nodes."""
        results = {}
        for node_name in self._contracts:
            errors = self.verify_node(node_name)
            if errors:
                results[node_name] = errors
        return results
    
    def get_capability_matrix(self) -> Dict[str, Set[CapabilityType]]:
        """Get matrix of node requirements."""
        matrix = {}
        for node_name, contract in self._contracts.items():
            matrix[node_name] = {r.capability for r in contract.requirements}
        return matrix