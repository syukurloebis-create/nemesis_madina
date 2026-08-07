# backend/domain/enums/finding.py
"""
Finding Domain Enums

Matches PostgreSQL ENUM 'findingstatus' values.
"""

import enum


class FindingStatus(str, enum.Enum):
    """Status of a finding. Matches PostgreSQL ENUM 'findingstatus'."""
    
    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"