# backend/cache/memory_cache.py

from typing import Optional, Any, Dict
import asyncio
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field

from backend.cache.provider import CacheProvider


@dataclass(slots=True, frozen=True)
class CacheEntry:
    """Cache entry with TTL."""
    key: str
    value: Any
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ttl_seconds: int = 60


class MemoryCache(CacheProvider):
    """In-memory cache implementation."""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 60):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            entry = self._cache.get(key)
            if entry and not self._is_expired(entry):
                return entry.value
            if entry:
                del self._cache[key]
            return None
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        async with self._lock:
            if len(self._cache) >= self._max_size:
                self._evict_oldest()
            
            ttl = ttl_seconds or self._default_ttl
            self._cache[key] = CacheEntry(key=key, value=value, ttl_seconds=ttl)
    
    async def delete(self, key: str) -> None:
        async with self._lock:
            self._cache.pop(key, None)
    
    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()
    
    async def exists(self, key: str) -> bool:
        async with self._lock:
            entry = self._cache.get(key)
            return entry is not None and not self._is_expired(entry)
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        age = (datetime.now(timezone.utc) - entry.created_at).total_seconds()
        return age > entry.ttl_seconds
    
    def _evict_oldest(self):
        if self._cache:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
            del self._cache[oldest_key]