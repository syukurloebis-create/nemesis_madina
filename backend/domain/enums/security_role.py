"""Security Role Enum - Canonical Definition

SEC-4.7 Frozen Contract:
- Single source of truth for authorization roles
- Replaces UserRole and Role enums
- AUDITOR merged into INVESTIGATOR
- reviewer, examiner removed
"""

from enum import Enum


class SecurityRole(str, Enum):
    """Canonical security roles for NEMESIS."""
    
    ADMIN = "ADMIN"
    INVESTIGATOR = "INVESTIGATOR"
    IRBAN = "IRBAN"
    INSPEKTUR = "INSPEKTUR"
    EXECUTIVE = "EXECUTIVE"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"
    
    @classmethod
    def from_legacy(cls, value: str) -> "SecurityRole":
        """Convert legacy role values to canonical SecurityRole.
    
        Raises:
            ValueError: If role value is not recognized.
        """
        mapping = {
            "admin": cls.ADMIN,
            "ADMIN": cls.ADMIN,
            "investigator": cls.INVESTIGATOR,
            "INVESTIGATOR": cls.INVESTIGATOR,
            "analyst": cls.ANALYST,
            "ANALYST": cls.ANALYST,
            "viewer": cls.VIEWER,
            "VIEWER": cls.VIEWER,
            "auditor": cls.INVESTIGATOR,
            "AUDITOR": cls.INVESTIGATOR,
            "irban": cls.IRBAN,
            "IRBAN": cls.IRBAN,
            "inspektur": cls.INSPEKTUR,
            "INSPEKTUR": cls.INSPEKTUR,
            "executive": cls.EXECUTIVE,
            "EXECUTIVE": cls.EXECUTIVE,
        }
    
        try:
            return mapping[value]
        except KeyError:
            raise ValueError(f"Invalid role: {value}")
    
    @classmethod
    def values(cls) -> list:
        """Get all role values as strings."""
        return [r.value for r in cls]