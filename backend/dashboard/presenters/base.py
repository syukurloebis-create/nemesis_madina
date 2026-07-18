# backend/dashboard/presenters/base.py

from typing import Protocol, TypeVar, Generic

T = TypeVar('T', covariant=True)
R = TypeVar('R', covariant=True)


class Presenter(Protocol[T, R]):
    """Presenter protocol - converts domain to response."""
    
    def present(self, data: T) -> R:
        """Present domain data as response model."""
        ...