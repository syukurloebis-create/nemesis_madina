"""
Graph Infrastructure - Persistence Strategies
"""

from enum import Enum, auto


class SaveStrategy(Enum):
    """Save strategies for graph persistence."""
    REPLACE = auto()
    MERGE = auto()
    APPEND = auto()
    UPSERT = auto()


class DeleteStrategy(Enum):
    """Delete strategies for graph deletion."""
    CASCADE = auto()
    SOFT_DELETE = auto()
    ARCHIVE = auto()
