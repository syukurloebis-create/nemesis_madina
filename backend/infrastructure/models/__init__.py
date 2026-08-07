"""
ORM Models Registry
Single import point for SQLAlchemy metadata discovery
"""

# Import all models to register them with Base
from backend.infrastructure.models.projection_checkpoint import ProjectionCheckpointModel
from backend.infrastructure.models.read_models import DashboardView
from backend.models.user import User

# Import cases models if exists
try:
    from backend.cases.models import Case, CaseEvent
except ImportError:
    pass

__all__ = [
    "ProjectionCheckpointModel",
    "DashboardView",
    "User",
]
