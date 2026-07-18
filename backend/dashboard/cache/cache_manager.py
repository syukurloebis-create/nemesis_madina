# backend/dashboard/cache/cache_manager.py

from typing import Optional, Any, Dict
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
import asyncio
import hashlib
import json

from backend.telemetry.metrics import record_pipeline_execution


@dataclass(slots=True, frozen=True)
class CacheEntry:
    """Cache entry with TTL."""
    key: str
    value: Any
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ttl_seconds: int = 60
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        age = (datetime.now(timezone.utc) - self.created_at).total_seconds()
        return age > self.ttl_seconds


class CacheManager:
    """
    In-memory cache manager for dashboard data.
    
    Supports TTL, LRU eviction, and cache invalidation.
    """
    
    def __init__(self, max_size: int = 100, default_ttl: int = 60):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired:
                return entry.value
            if entry:
                del self._cache[key]
            return None
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Set value in cache."""
        async with self._lock:
            # Check size limit
            if len(self._cache) >= self._max_size:
                self._evict_oldest()
            
            ttl = ttl_seconds or self._default_ttl
            self._cache[key] = CacheEntry(
                key=key,
                value=value,
                ttl_seconds=ttl
            )
    
    async def invalidate(self, key: str):
        """Invalidate a cache entry."""
        async with self._lock:
            self._cache.pop(key, None)
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate all cache entries matching pattern."""
        async with self._lock:
            keys_to_delete = [key for key in self._cache if pattern in key]
            for key in keys_to_delete:
                del self._cache[key]
    
    async def clear(self):
        """Clear all cache."""
        async with self._lock:
            self._cache.clear()
    
    def _evict_oldest(self):
        """Evict the oldest cache entry."""
        if self._cache:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
            del self._cache[oldest_key]
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from prefix and kwargs."""
        sorted_items = sorted(kwargs.items())
        key_string = f"{prefix}:{json.dumps(sorted_items)}"
        return hashlib.md5(key_string.encode()).hexdigest()


# Cache decorator
def cached(ttl_seconds: int = 60, prefix: str = "cache"):
    """Decorator for caching function results."""
    def decorator(func):
        cache_manager = CacheManager()
        
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache_manager._generate_key(prefix, **kwargs)
            
            # Try cache
            cached_value = await cache_manager.get(key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache_manager.set(key, result, ttl_seconds)
            
            return result
        
        return wrapper
    
    return decorator