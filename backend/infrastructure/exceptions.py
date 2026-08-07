# backend/infrastructure/exceptions.py
"""
Repository Exceptions — Layer untuk membungkus exception infrastructure.
"""

from typing import Optional, Any, Dict


class RepositoryError(Exception):
    """
    Base exception for repository errors.
    
    Supports metadata for audit, tracing, and observability.
    """
    
    def __init__(
        self,
        message: Optional[str] = None,
        *,
        operation: Optional[str] = None,
        repository: Optional[str] = None,
        case_id: Optional[str] = None,
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        # Build message
        if message is None:
            msg_parts = []
            if operation:
                msg_parts.append(f"Operation: {operation}")
            if repository:
                msg_parts.append(f"Repository: {repository}")
            if case_id:
                msg_parts.append(f"Case: {case_id}")
            message = " | ".join(msg_parts) if msg_parts else "Repository error occurred"
        
        self.message = message
        self.operation = operation
        self.repository = repository
        self.case_id = case_id
        self.original_error = original_error
        self.metadata = kwargs
        
        super().__init__(message)
    
    def __str__(self) -> str:
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging and audit."""
        result = {
            "message": self.message,
            "operation": self.operation,
            "repository": self.repository,
            "case_id": self.case_id,
        }
        if self.original_error:
            result["original_error"] = str(self.original_error)
        if self.metadata:
            result.update(self.metadata)
        return result


class SQLExecutionError(RepositoryError):
    """Exception for SQL execution failures."""

    def __init__(
        self,
        message: str,
        *,
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            original_error=original_error,
            **kwargs
        )


class SQLNotFoundError(RepositoryError):
    """Exception when SQL query not found."""

    def __init__(self, key: str):
        self.key = key
        super().__init__(f"SQL query not found: {key}")


class RepositoryValidationError(RepositoryError):
    """Exception when repository data validation fails."""

    def __init__(
        self,
        message: str,
        *,
        field: Optional[str] = None,
        **kwargs
    ):
        self.field = field
        super().__init__(
            message=message,
            field=field,
            **kwargs
        )