"""
Domain Services Assembler — Create all domain services.
"""

from backend.services.domain.confidence_calculator import ConfidenceCalculator
from backend.services.domain.status_calculator import StatusCalculator


def create_domain_services():
    """Create all domain services."""
    return {
        "confidence": ConfidenceCalculator(),
        "status": StatusCalculator(),
    }