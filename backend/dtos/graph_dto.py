"""
Graph DTOs - Compatibility Wrapper

Phase B: Wrapper created
Phase C: Dual registration
Phase D: Import migration
Phase E: Legacy removal

This is a COMPATIBILITY LAYER only.
DO NOT add business logic.
DO NOT change behavior.
DO NOT modify return values.
DO NOT change exceptions.

Purpose: Enable phased migration from legacy graph/application/dto
to platform backend/dtos/graph_dto.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from uuid import UUID


# Re-export all DTOs from legacy
from backend.graph.application.dto import (
    GraphBuildRequest as _GraphBuildRequest,
    VendorDTO as _VendorDTO,
    PackageDTO as _PackageDTO,
    OfficerDTO as _OfficerDTO,
    InstitutionDTO as _InstitutionDTO,
    RelationshipDTO as _RelationshipDTO,
)


# Re-export with same names
GraphBuildRequest = _GraphBuildRequest
VendorDTO = _VendorDTO
PackageDTO = _PackageDTO
OfficerDTO = _OfficerDTO
InstitutionDTO = _InstitutionDTO
RelationshipDTO = _RelationshipDTO


# For backward compatibility, expose all DTOs
__all__ = [
    "GraphBuildRequest",
    "VendorDTO",
    "PackageDTO",
    "OfficerDTO",
    "InstitutionDTO",
    "RelationshipDTO",
]