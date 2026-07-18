"""
NEMESIS Madina - Trace ID Value Object
"""

from backend.domain.value_objects.base_uuid import BaseUUID


class TraceId(BaseUUID):
    """Trace ID - for distributed tracing."""
    pass