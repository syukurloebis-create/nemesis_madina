"""
NEMESIS Madina - Correlation ID Value Object
"""

from backend.domain.value_objects.base_uuid import BaseUUID


class CorrelationId(BaseUUID):
    """Correlation ID - for request correlation."""
    pass