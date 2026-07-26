# backend/application/dto/procurement_record.py

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ProcurementRecord:
    """Immutable DTO for procurement data."""
    
    vendor_name: str
    package_code: str
    package_name: str
    institution_name: str
    sub_unit: str
    year: int
    value: float
    method: str
    transaction_source: str
    funding_source: str
    procurement_type: str
    status: str
    ppk: Optional[str] = None