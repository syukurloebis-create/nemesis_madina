# backend/cache/provider.py

from typing import Protocol, Optional, Any, TypeVar, Generic
from abc import ABC, abstractmethod

T = TypeVar('T')


class CacheProvider(Protocol):
    """Protocol for cache providers."""
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        ...
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set value in cache."""
        ...
    
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        ...
    
    async def clear(self) -> None:
        """Clear all cache."""
        ...
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        ...