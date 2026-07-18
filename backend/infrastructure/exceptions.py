"""
Repository Exceptions — Layer untuk membungkus exception infrastructure.
"""

from typing import Optional


class RepositoryError(Exception):
    """Base exception for repository errors."""
    pass


class SQLExecutionError(RepositoryError):
    """Exception for SQL execution failures."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)


class SQLNotFoundError(RepositoryError):
    """Exception when SQL query not found."""
    
    def __init__(self, key: str):
        self.key = key
        super().__init__(f"SQL query not found: {key}")


class RepositoryValidationError(RepositoryError):
    """Exception when repository data validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message)