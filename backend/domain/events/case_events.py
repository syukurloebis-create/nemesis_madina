"""
Sprint 1 Case Events - Legacy Compatibility
Uses new DomainEvent base from Sprint 2 foundation.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from .base import DomainEvent  # ✅ Import from new base
from .metadata import EventMetadata


@dataclass(frozen=True)
class CaseCreated:
    case_id: UUID
    title: str
    description: Optional[str] = None
    created_by: Optional[str] = None


@dataclass(frozen=True)
class CaseUpdated:
    case_id: UUID
    changes: dict
    updated_by: Optional[str] = None


@dataclass(frozen=True)
class CaseStatusChanged:
    case_id: UUID
    old_status: str
    new_status: str
    changed_by: Optional[str] = None


@dataclass(frozen=True)
class CaseAssigned:
    case_id: UUID
    assigned_to: str
    assigned_by: Optional[str] = None


@dataclass(frozen=True)
class CaseClosed:
    case_id: UUID
    reason: Optional[str] = None
    closed_by: Optional[str] = None