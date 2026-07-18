# backend/cache/no_cache.py

from typing import Optional, Any

from backend.cache.provider import CacheProvider


class NoCache(CacheProvider):
    """No-op cache implementation."""
    
    async def get(self, key: str) -> Optional[Any]:
        return None
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        pass
    
    async def delete(self, key: str) -> None:
        pass
    
    async def clear(self) -> None:
        pass
    
    async def exists(self, key: str) -> bool:
        return False