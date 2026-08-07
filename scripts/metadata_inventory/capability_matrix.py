# capability_matrix.py
from typing import Dict, List, Set, Any
from dataclasses import dataclass
import sqlalchemy

@dataclass
class Capability:
    name: str
    min_version: str
    max_version: str
    description: str
    api_path: str

class CapabilityMatrix:
    """SQLAlchemy version capability matrix."""
    
    CAPABILITIES = [
        Capability(
            name="declarative_base",
            min_version="1.4.0",
            max_version="2.1.0",
            description="declarative_base() function",
            api_path="sqlalchemy.orm.declarative_base"
        ),
        Capability(
            name="declarative_base_class",
            min_version="2.0.0",
            max_version="2.1.0",
            description="DeclarativeBase class (2.0+)",
            api_path="sqlalchemy.orm.DeclarativeBase"
        ),
        Capability(
            name="registry",
            min_version="1.4.0",
            max_version="2.1.0",
            description="registry object",
            api_path="sqlalchemy.orm.registry"
        ),
        Capability(
            name="mapped_as_dataclass",
            min_version="2.0.0",
            max_version="2.1.0",
            description="MappedAsDataclass mixin",
            api_path="sqlalchemy.orm.MappedAsDataclass"
        ),
        Capability(
            name="extension_type",
            min_version="1.4.0",
            max_version="2.1.0",
            description="InspectionAttr.extension_type",
            api_path="sqlalchemy.orm.InspectionAttr.extension_type"
        ),
        Capability(
            name="all_orm_descriptors",
            min_version="2.0.0",
            max_version="2.1.0",
            description="inspect().all_orm_descriptors",
            api_path="sqlalchemy.inspect().all_orm_descriptors"
        ),
        Capability(
            name="association_proxy",
            min_version="1.4.0",
            max_version="2.1.0",
            description="association_proxy()",
            api_path="sqlalchemy.ext.associationproxy.association_proxy"
        ),
        Capability(
            name="hybrid_property",
            min_version="1.4.0",
            max_version="2.1.0",
            description="hybrid_property()",
            api_path="sqlalchemy.ext.hybrid.hybrid_property"
        ),
        Capability(
            name="selectinload",
            min_version="1.4.0",
            max_version="2.1.0",
            description="selectinload loader option",
            api_path="sqlalchemy.orm.selectinload"
        ),
        Capability(
            name="joinedload_attribute",
            min_version="2.0.0",
            max_version="2.1.0",
            description="joinedload(getattr(...)) for attribute",
            api_path="sqlalchemy.orm.joinedload"
        ),
    ]
    
    @classmethod
    def get_supported_capabilities(cls, version: str = None) -> List[Capability]:
        """Get capabilities supported by current SQLAlchemy version."""
        if version is None:
            version = sqlalchemy.__version__
        
        supported = []
        for cap in cls.CAPABILITIES:
            if cls._version_satisfies(version, cap.min_version, cap.max_version):
                supported.append(cap)
        
        return supported
    
    @classmethod
    def _version_satisfies(cls, version: str, min_version: str, max_version: str) -> bool:
        """Check if version satisfies range."""
        def parse(v):
            return tuple(int(x) for x in v.split('.'))
        
        current = parse(version)
        min_v = parse(min_version)
        max_v = parse(max_version)
        
        return min_v <= current <= max_v
    
    @classmethod
    def get_deprecated_capabilities(cls, version: str = None) -> List[Capability]:
        """Get capabilities deprecated in current version."""
        if version is None:
            version = sqlalchemy.__version__
        
        deprecated = []
        for cap in cls.CAPABILITIES:
            if not cls._version_satisfies(version, cap.min_version, cap.max_version):
                deprecated.append(cap)
        
        return deprecated
    
    @classmethod
    def get_capability_matrix(cls) -> Dict[str, Dict[str, str]]:
        """Get full capability matrix."""
        matrix = {}
        for cap in cls.CAPABILITIES:
            matrix[cap.name] = {
                "min_version": cap.min_version,
                "max_version": cap.max_version,
                "description": cap.description,
                "api_path": cap.api_path
            }
        return matrix