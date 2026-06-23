# DEPRECATED - Use backend.graph instead
import warnings
warnings.warn(
    "This module is deprecated. Use 'from graph import ...'",
    DeprecationWarning,
    stacklevel=2
)

from graph import *

__all__ = [
    'RelationshipGraph',
    'CollusionDetector',
    'QueryBuilder',
    'GraphMetrics'
]
