"""
Graph Application - DTOs

Data Transfer Objects for Application Layer.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from uuid import UUID


@dataclass(frozen=True)
class VendorDTO:
    """Vendor data."""
    npwp: str
    name: str
    address: Optional[str] = None
    sector: Optional[str] = None
    registration_date: Optional[str] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PackageDTO:
    """Package data."""
    package_code: str
    name: str
    value: Optional[float] = None
    procuring_institution: Optional[str] = None
    procurement_method: Optional[str] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OfficerDTO:
    """Officer data."""
    nip: str
    name: str
    position: Optional[str] = None
    institution: Optional[str] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class InstitutionDTO:
    """Institution data."""
    id: str
    name: str
    type: Optional[str] = None
    address: Optional[str] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RelationshipDTO:
    """Relationship data."""
    source: str
    target: str
    relationship_type: str
    weight: float = 1.0
    amount: Optional[float] = None
    description: Optional[str] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphBuildRequest:
    """Build request DTO."""
    case_id: UUID
    institution_id: UUID
    vendors: List[VendorDTO] = field(default_factory=list)
    packages: List[PackageDTO] = field(default_factory=list)
    officers: List[OfficerDTO] = field(default_factory=list)
    institutions: List[InstitutionDTO] = field(default_factory=list)
    relationships: List[RelationshipDTO] = field(default_factory=list)