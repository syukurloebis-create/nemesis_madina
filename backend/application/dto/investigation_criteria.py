# backend/application/dto/investigation_criteria.py

from dataclasses import dataclass
from typing import Tuple
from uuid import UUID


@dataclass(frozen=True)
class InvestigationCriteria:
    """
    Immutable DTO for investigation scope.
    
    ✅ Business-oriented (not database column names)
    ✅ Institution IDs (not names) for future compatibility
    ✅ Supports fallback to names during migration
    """
    
    case_id: UUID
    institutions: Tuple[str, ...] = ()      # institution_ids
    vendors: Tuple[str, ...] = ()           # vendor_names
    packages: Tuple[str, ...] = ()          # package_codes
    years: Tuple[int, ...] = ()

    @classmethod
    def empty(cls, case_id: UUID) -> "InvestigationCriteria":
        return cls(case_id=case_id)