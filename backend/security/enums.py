# backend/security/enums.py

"""
Security Domain Enums
"""

import enum


class UserRole(str, enum.Enum):
    """User role enum - canonical definition."""
    
    ADMIN = "admin"
    INVESTIGATOR = "investigator"
    ANALYST = "analyst"
    VIEWER = "viewer"
    AUDITOR = "auditor"
