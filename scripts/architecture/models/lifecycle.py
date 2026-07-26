# scripts/architecture/models/lifecycle.py
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum

@dataclass 
class CapabilityLifecycle(Enum):
    """Full capability lifecycle states"""
    
    PLANNED = "planned"
    """Conceptual - not yet developed"""
    
    EXPERIMENTAL = "experimental"
    """Initial implementation, not stable"""
    
    DEVELOPMENT = "development"
    """Active development, not production ready"""
    
    BETA = "beta"
    """Feature complete, limited testing"""
    
    PRODUCTION = "production"
    """Production ready, fully supported"""
    
    DEPRECATED = "deprecated"
    """Still available but will be removed"""
    
    REMOVED = "removed"
    """No longer available"""
    
    @classmethod
    def is_active(cls, state: 'CapabilityLifecycle') -> bool:
        """Check if capability is active"""
        return state not in [cls.DEPRECATED, cls.REMOVED]
    
    @classmethod
    def is_production_ready(cls, state: 'CapabilityLifecycle') -> bool:
        """Check if capability is production ready"""
        return state in [cls.PRODUCTION, cls.BETA]
    
    @classmethod
    def can_depend_on(cls, state: 'CapabilityLifecycle', 
                      dep_state: 'CapabilityLifecycle') -> bool:
        """Check if capability can depend on another"""
        # Can't depend on deprecated or removed
        if dep_state in [cls.DEPRECATED, cls.REMOVED]:
            return False
        # Experimental can depend on anything (except deprecated)
        return True

@dataclass
class CapabilityWithLifecycle:
    """Capability with lifecycle tracking"""
    id: str
    name: str
    owner: str
    lifecycle: CapabilityLifecycle
    depends_on: List[str]
    modules: List[str]
    metadata: Dict[str, Any] = None
    
    def is_healthy(self) -> bool:
        """Check if capability is healthy"""
        return self.lifecycle in [CapabilityLifecycle.PRODUCTION, 
                                  CapabilityLifecycle.BETA]
    
    def get_deprecation_warning(self) -> Optional[str]:
        """Get deprecation warning if applicable"""
        if self.lifecycle == CapabilityLifecycle.DEPRECATED:
            return f"Capability {self.id} is deprecated"
        if self.lifecycle == CapabilityLifecycle.REMOVED:
            return f"Capability {self.id} has been removed"
        return None