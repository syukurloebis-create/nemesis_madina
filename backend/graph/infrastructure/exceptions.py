"""
Graph Infrastructure - Exceptions
"""


class OptimisticLockError(Exception):
    """Raised when version conflict occurs during save."""
    pass


class GraphNotFoundError(Exception):
    """Raised when graph data is not found."""
    pass


class GraphPersistenceError(Exception):
    """Raised when persistence operation fails."""
    pass