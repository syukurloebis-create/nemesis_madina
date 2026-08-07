# capability_negotiation.py
import inspect
import sqlalchemy
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class DiscoveredCapability:
    name: str
    available: bool
    api_path: str
    version_introduced: str
    version_deprecated: Optional[str] = None

class CapabilityNegotiator:
    """Runtime capability discovery and negotiation."""
    
    def __init__(self):
        self.discovered: Dict[str, DiscoveredCapability] = {}
        self.sqlalchemy_version = sqlalchemy.__version__
    
    def discover(self) -> Dict[str, DiscoveredCapability]:
        """Discover capabilities at runtime."""
        
        # Check for declarative_base
        try:
            from sqlalchemy.orm import declarative_base
            self.discovered["declarative_base"] = DiscoveredCapability(
                name="declarative_base",
                available=True,
                api_path="sqlalchemy.orm.declarative_base",
                version_introduced="1.4.0"
            )
        except ImportError:
            self.discovered["declarative_base"] = DiscoveredCapability(
                name="declarative_base",
                available=False,
                api_path="sqlalchemy.orm.declarative_base",
                version_introduced="1.4.0"
            )
        
        # Check for DeclarativeBase
        try:
            from sqlalchemy.orm import DeclarativeBase
            self.discovered["DeclarativeBase"] = DiscoveredCapability(
                name="DeclarativeBase",
                available=True,
                api_path="sqlalchemy.orm.DeclarativeBase",
                version_introduced="2.0.0"
            )
        except ImportError:
            self.discovered["DeclarativeBase"] = DiscoveredCapability(
                name="DeclarativeBase",
                available=False,
                api_path="sqlalchemy.orm.DeclarativeBase",
                version_introduced="2.0.0"
            )
        
        # Check for MappedAsDataclass
        try:
            from sqlalchemy.orm import MappedAsDataclass
            self.discovered["MappedAsDataclass"] = DiscoveredCapability(
                name="MappedAsDataclass",
                available=True,
                api_path="sqlalchemy.orm.MappedAsDataclass",
                version_introduced="2.0.0"
            )
        except ImportError:
            self.discovered["MappedAsDataclass"] = DiscoveredCapability(
                name="MappedAsDataclass",
                available=False,
                api_path="sqlalchemy.orm.MappedAsDataclass",
                version_introduced="2.0.0"
            )
        
        # Check for AssociationProxy
        try:
            from sqlalchemy.ext.associationproxy import AssociationProxy
            self.discovered["AssociationProxy"] = DiscoveredCapability(
                name="AssociationProxy",
                available=True,
                api_path="sqlalchemy.ext.associationproxy.AssociationProxy",
                version_introduced="1.4.0"
            )
        except ImportError:
            self.discovered["AssociationProxy"] = DiscoveredCapability(
                name="AssociationProxy",
                available=False,
                api_path="sqlalchemy.ext.associationproxy.AssociationProxy",
                version_introduced="1.4.0"
            )
        
        # Check for hybrid_property
        try:
            from sqlalchemy.ext.hybrid import hybrid_property
            self.discovered["hybrid_property"] = DiscoveredCapability(
                name="hybrid_property",
                available=True,
                api_path="sqlalchemy.ext.hybrid.hybrid_property",
                version_introduced="1.4.0"
            )
        except ImportError:
            self.discovered["hybrid_property"] = DiscoveredCapability(
                name="hybrid_property",
                available=False,
                api_path="sqlalchemy.ext.hybrid.hybrid_property",
                version_introduced="1.4.0"
            )
        
        # Check for inspect with all_orm_descriptors
        try:
            from sqlalchemy import inspect
            # Create a test class to check
            from sqlalchemy.orm import declarative_base
            Base = declarative_base()
            
            class Test(Base):
                __tablename__ = "test"
                id = None
            
            insp = inspect(Test)
            has_descriptors = hasattr(insp, 'all_orm_descriptors')
            
            self.discovered["all_orm_descriptors"] = DiscoveredCapability(
                name="all_orm_descriptors",
                available=has_descriptors,
                api_path="sqlalchemy.inspect().all_orm_descriptors",
                version_introduced="2.0.0"
            )
        except Exception:
            self.discovered["all_orm_descriptors"] = DiscoveredCapability(
                name="all_orm_descriptors",
                available=False,
                api_path="sqlalchemy.inspect().all_orm_descriptors",
                version_introduced="2.0.0"
            )
        
        # Check for selectinload
        try:
            from sqlalchemy.orm import selectinload
            self.discovered["selectinload"] = DiscoveredCapability(
                name="selectinload",
                available=True,
                api_path="sqlalchemy.orm.selectinload",
                version_introduced="1.4.0"
            )
        except ImportError:
            self.discovered["selectinload"] = DiscoveredCapability(
                name="selectinload",
                available=False,
                api_path="sqlalchemy.orm.selectinload",
                version_introduced="1.4.0"
            )
        
        # Check for registry
        try:
            from sqlalchemy.orm import registry
            self.discovered["registry"] = DiscoveredCapability(
                name="registry",
                available=True,
                api_path="sqlalchemy.orm.registry",
                version_introduced="1.4.0"
            )
        except ImportError:
            self.discovered["registry"] = DiscoveredCapability(
                name="registry",
                available=False,
                api_path="sqlalchemy.orm.registry",
                version_introduced="1.4.0"
            )
        
        return self.discovered
    
    def get_available(self) -> List[str]:
        """Get list of available capabilities."""
        return [name for name, cap in self.discovered.items() if cap.available]
    
    def negotiate(self, required: List[str]) -> Dict[str, Any]:
        """Negotiate capabilities with requirements."""
        self.discover()
        
        results = {}
        for req in required:
            cap = self.discovered.get(req)
            if cap:
                results[req] = {
                    "available": cap.available,
                    "version_introduced": cap.version_introduced,
                    "version_deprecated": cap.version_deprecated
                }
            else:
                results[req] = {"available": False}
        
        all_available = all(v["available"] for v in results.values())
        
        return {
            "sqlalchemy_version": self.sqlalchemy_version,
            "capabilities": results,
            "all_available": all_available,
            "missing": [k for k, v in results.items() if not v["available"]]
        }