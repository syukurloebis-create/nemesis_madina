# scripts/metadata_inventory/__init__.py
"""
ORM Verification Platform L4 - Enterprise Verification Framework.
"""

__version__ = "1.0.0"
__status__ = "Phase 1 - Core Infrastructure (Complete)"

# Core modules (lightweight)
from typing import Dict, List, Optional, Any, Callable, Type 
from .canonical_serializer import CanonicalSerializer, Fingerprint
from .contracts import (
    ArtifactId, ArtifactEnvelope, ArtifactContract,
    Dependency, DependencyType, NodeDefinition, ExecutionRecord
)

# Lazy imports for heavy modules
# Import these only when needed, not at package load

__all__ = [
    '__version__',
    '__status__',
    'CanonicalSerializer',
    'Fingerprint',
    'ArtifactId',
    'ArtifactEnvelope',
    'ArtifactContract',
    'Dependency',
    'DependencyType',
    'NodeDefinition',
    'ExecutionRecord',
]


# Lazy loader for heavy modules
def __getattr__(name):
    """Lazy import for heavy modules."""
    if name in ['TypedDAG', 'VerificationEngine', 'RuleRegistry', 'ALL_RULES']:
        if name == 'TypedDAG':
            from .typed_dag import TypedDAG
            return TypedDAG
        elif name == 'VerificationEngine':
            from .verification.engine import VerificationEngine
            return VerificationEngine
        elif name == 'RuleRegistry':
            from .verification.registry import RuleRegistry
            return RuleRegistry
        elif name == 'ALL_RULES':
            from .verification.rules import ALL_RULES
            return ALL_RULES
    raise AttributeError(f"module {__name__} has no attribute {name}")