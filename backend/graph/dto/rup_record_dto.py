# backend/graph/dto/rup_record_dto.py

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass(frozen=True)
class RupRecordDTO:
    """RUP record DTO - 1:1 from rup_paket_detailed.

    Contract R16.4.4:
        - id: source_id (1:1)
        - business_key = "RUP:" + str(id)
        - Monetary values: Decimal (NOT float)
    """

    # Identity & Provenance (required)
    id: int
    package_code: str
    name: str
    vendor: str
    year: int

    # Optional source metadata
    rup_code: Optional[str] = None

    # Monetary (Decimal, NOT float)
    total_value: Optional[Decimal] = None
    pdn_value: Optional[Decimal] = None

    # Metadata
    institution: Optional[str] = None
    work_unit: Optional[str] = None
    fund_source: Optional[str] = None
    procurement_method: Optional[str] = None
    procurement_type: Optional[str] = None
    status: Optional[str] = None
    transaction_source: Optional[str] = None