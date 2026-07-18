"""
Risk Level Normalizer - Single Source of Truth.

Converts database values to domain RiskLevel enum.
"""

from backend.domain.enums.risk_level import RiskLevel


def normalize_risk_level(level: str) -> RiskLevel:
    """
    Normalize database risk level to domain enum.

    Args:
        level: Raw level from database (e.g., "INFO", "LOW", "HIGH", etc.)

    Returns:
        Normalized RiskLevel enum.

    Mapping:
        INFO → UNKNOWN (if INFO is not in domain model)
        UNKNOWN → UNKNOWN
        LOW → LOW
        MEDIUM → MEDIUM
        HIGH → HIGH
        CRITICAL → CRITICAL
    """
    if not level:
        return RiskLevel.UNKNOWN

    mapping = {
        "INFO": RiskLevel.UNKNOWN,
        "UNKNOWN": RiskLevel.UNKNOWN,
        "LOW": RiskLevel.LOW,
        "MEDIUM": RiskLevel.MEDIUM,
        "HIGH": RiskLevel.HIGH,
        "CRITICAL": RiskLevel.CRITICAL,
    }

    return mapping.get(level.upper(), RiskLevel.UNKNOWN)


def normalize_risk_level_str(level: str) -> str:
    """
    Normalize database level to domain enum string.

    Convenience function for string-based mapping.
    """
    return normalize_risk_level(level).value